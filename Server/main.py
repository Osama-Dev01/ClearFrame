# main.py
import time
import json
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from urllib.parse import urlparse
from simhash import TweetMatchingSystem
from database import engine, get_db, Base
from models import (
    User,
    ApprovalStatus,
    VerificationResult,
    VerificationSource,
    Tweet,
    VerificationStatus
)
from filters import validate_tweet
from admin.admin_routes import router as admin_router
from member.member_routes import router as member_router

from normalize import normalize_tweet
from xlmmodel import ModelManager
from factualmodel import FactualityClassifier
from crossverify import cross_verify


# -------------------------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TweetPlug Verification Backend", version="2.1")

# -------------------------------------------------------------------
# CORS SETTINGS
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# MODEL INITIALIZATION
# -------------------------------------------------------------------
model_manager = ModelManager()
factuality_model = FactualityClassifier()

# Print to verify crossverify module loaded


@app.on_event("startup")
async def load_models_on_startup():
    print("="*60)
    print("Loading classification and factuality models...")
    model_manager.load_model()
    factuality_model.load_model()
    print("Classification and factuality models loaded.\n")
    print("="*60)
    # Load cross-verification models
  


# -------------------------------------------------------------------
# MAIN ENDPOINT — RECEIVE & VERIFY TWEET
# -------------------------------------------------------------------
@app.post("/receive-tweet")
async def classify_tweet_endpoint(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        tweet_text = data.get("tweet_text")
        author_handle = data.get("author_handle", None)
        tweet_date_str = data.get("tweet_date")  # "2025-10-09T18:11:13.000Z"
        tweet_date = None
        if tweet_date_str:
            try:
                dt = datetime.fromisoformat(tweet_date_str.replace("Z", "+00:00"))  # convert to UTC datetime
                tweet_date = dt.strftime("%Y-%m-%d")  # get date only
            except Exception as e:
                print(f"Invalid tweet_date format: {e}")
        if not tweet_text:
            raise HTTPException(status_code=400, detail="No tweet_text provided.")

        print("\n" + "=" * 80)
        print(f"New Tweet received!!\n By: {author_handle} dated: {tweet_date}\n")
        print("=" * 80)
        print(f"Original text of the tweet:\n{tweet_text}\n")
        print("-" * 80)

        # ------------------- VALIDATION -------------------
        tweet_text = tweet_text.encode('utf-8').decode('utf-8')
        is_valid, reason = validate_tweet(tweet_text)

        if not is_valid:
            print(f"VALIDATION FAILED → {reason}\n")
            print("=" * 80 + "\n")
            return {"status": "not_valid", "message": reason}

        print("VALIDATION PASSED!\n")
        print("-" * 80)

        # ------------------- NORMALIZATION -------------------
        normalized_tweet = normalize_tweet(tweet_text)
        if not normalized_tweet or len(normalized_tweet.strip()) < 5:
            print("NORMALIZATION FAILED (Tweet too short after cleanup)\n")
            print("=" * 80 + "\n")
            return {"status": "not_valid", "message": "Tweet too short after normalization"}

        print(f"Normalized text:\n{normalized_tweet}\n")
        print("-" * 80)

        # ------------------- CATEGORY CLASSIFICATION -------------------
        print("Running classifier...")
        predicted_class_id = model_manager.predict(normalized_tweet)
        label_map = {
            0: 'cricket',
            1: 'economy',
            2: 'international_relations',
            3: 'others',
            4: 'politics'
        }
        predicted_label = label_map.get(predicted_class_id, "unknown")

        print(f"Predicted Category: {predicted_label.upper()} (ID: {predicted_class_id})")
        print("=" * 80 + "\n")

        if predicted_label == "others":
            print(f"Rejected\n Reason:\n Category: Others")
            print("=" * 80 + "\n")
            return {
                "status": "not_valid",
                "message": "Tweet not valid for verification"
            }

        # ------------------- FACTUALITY CHECK -------------------
        print("Running factuality check...")
        factuality_result = factuality_model.predict(normalized_tweet, return_probs=True)

        factual_label = str(factuality_result.get("prediction", "")).strip()
        probs = factuality_result.get("probabilities", {}) or {}

        # Extract confidence for predicted label
        factual_conf = probs.get(factual_label, 0.0)
        if factual_conf > 1.0:
            factual_conf /= 100.0

        print(f"Factuality: {factual_label} ({factual_conf * 100:.2f}%)")
        print("=" * 80 + "\n")

        # ------------------- FACTUALITY DECISION -------------------
        # Only skip verification if clearly Non-Factual or very low confidence
        if factual_label.lower() == "non-factual" or factual_conf < 0.5:
            print(f"The tweet is non-Factual or low confidence ({factual_conf * 100:.2f}%) — skipping verification.")
            print("=" * 80 + "\n")
            return {
                "status": "valid",
                "message": "Tweet not suitable for verification (non-factual or uncertain)",
                "factuality": {
                    "prediction": factual_label,
                    "confidence": round(factual_conf, 4)
                }
            }


            # Initialize system
        matching_system = TweetMatchingSystem(db_session=db)
        matching_system.initialize()

        # Perform matching
        results = matching_system.match_tweet(normalized_tweet)
        print(f"Matching results: {results}")

        # Check if there are any matches
        if results and results.get("matches") and len(results["matches"]) > 0:
            # Get the best match (first match)
            matched = results["matches"][0]
            similarity = float(matched.get("similarity_score", 0))
            
            # Check if similarity is greater than or equal to 90%
            if similarity >= 90.0:
                # ✅ Similarity >= 90% - Return matched result
                verdict = (matched.get("verdict", "unverified")).strip().lower()
                matched_text = matched.get("matched_tweet_text", "")
                
                return {
                    "status": "ok",
                    "verification": {
                        "verdict": verdict,
                        "confidence_score": round(similarity, 2),
                        "sources": [
                            {
                                "tweet_id": matched.get("matched_tweet_id"),
                                "matched_text": matched_text,
                                "similarity": matched.get("similarity_score", 0.0)
                            }
                        ]
                    }
                }
            else:
                print(f"Similarity ({similarity}%) is below threshold (90%). Continuing...")
        else:
            print("No matches found. Continuing...")

        # Continue with other code
        print("Proceeding to other verification methods...")
        # YOUR OTHER CODE GOES HERE


  
        # ------------------- SAVE TWEET TO DB -------------------
        print("Storing tweet in database before verification...")
        print("=" * 80 + "\n")
        new_tweet = Tweet(
            user_id=1,
            tweet_text=normalized_tweet,
            verification_status=VerificationStatus.pending
        )
        db.add(new_tweet)
        db.commit()
        db.refresh(new_tweet)
        tweet_id = new_tweet.tweet_id
        print(f"Tweet saved (tweet_id = {tweet_id})")
        print("=" * 80 + "\n")
        
       

        # ------------------- CROSS VERIFICATION -------------------

        print("Running Cross Verification...")
        verification_report = cross_verify(
            tweet_text,
            db,
            author_handle,
            normalized_tweet
        )
        print("=" * 80 + "\n")
        
        # ------------------- SAVE VERIFICATION RESULT -------------------
        




        print("Saving verification results to database...")
        verif_result = VerificationResult(
            tweet_id=tweet_id,
            status="completed",
            confidence=str(verification_report.get("confidence_score", "")),
            verdict=verification_report.get("verdict", "Unverified"),
            factuality=factual_label
        )
        db.add(verif_result)
        db.commit()
        db.refresh(verif_result)

        # Save sources from verification report
        for src in verification_report.get("sources", []):
            # Extract domain (new simplified pipeline returns 'domain')
            source_name = src.get("domain", "")
            url = src.get("url", "")
            
            # The simplified pipeline returns 'evidence_sentence' instead of 'snippet'
            snippet = src.get("evidence_sentence", "")
            
            # Similarity is directly available
            similarity = str(src.get("similarity", ""))

            src_entry = VerificationSource(
                verification_id=verif_result.id,
                source=source_name,
                url=url,
                snippet=snippet,
                similarity=similarity
            )
            db.add(src_entry)
        db.commit()

        # Update tweet status
        # new_tweet.verification_status = VerificationStatus.verified
        db.commit()

        print(f"Verification Complete | {verification_report.get('verdict', '').upper()} | Confidence Score: {verification_report.get('confidence_score', 0)}")
        print("=" * 80 + "\n")
        
        # print final response
        final_response = {
            "status": "success",
            "message": "Tweet verified successfully.",
            "tweet_id": tweet_id,
            "original_tweet": tweet_text,
            "normalized_tweet": normalized_tweet,
            "category": {
                "label": predicted_label,
                "id": predicted_class_id
            },
            "factuality": {
                "prediction": factual_label,
                "confidence": round(factual_conf, 4)
            },
            "verification": verification_report
        }

        print("\nFINAL RESPONSE:")
        print(json.dumps(final_response, indent=4, ensure_ascii=False))
        print("=" * 80 + "\n")
        
        # ------------------- WRITE CLEAN LOG TO FILE -------------------
        try:
            log_path = "log.txt"
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write("\n" + "="*100 + "\n")
                log_file.write(f"Timestamp      : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                log_file.write(f"Tweet ID       : {tweet_id}\n")
                log_file.write(f"Author Handle  : {author_handle}\n")
                log_file.write(f"Tweet Date     : {tweet_date}\n")
                log_file.write(f"Tweet Text     : {tweet_text.strip()}\n")
                log_file.write("-"*100 + "\n")
                log_file.write(f"Predicted Category : {predicted_label.upper()} (ID: {predicted_class_id})\n")
                log_file.write(f"Factuality         : {factual_label} ({round(factual_conf*100,2)}%)\n")
                log_file.write(f"Verdict            : {verification_report.get('verdict', '')}\n")
                log_file.write(f"Confidence Score   : {verification_report.get('confidence_score', '')}\n")
                log_file.write("-"*100 + "\n")

                # Sources summary (top 3 shown)
                sources = verification_report.get("sources", [])
                if sources:
                    log_file.write("Top Evidence Sources:\n")
                    for i, src in enumerate(sources[:3], start=1):
                        # Extract data from simplified pipeline format
                        url = src.get("url", "Unknown")
                        domain = src.get("domain", "")
                        title = src.get("title", "")
                        snippet = src.get("evidence_sentence", "")[:150]
                        similarity = src.get("similarity", "")
                        nli_label = src.get("nli_label", "")
                        nli_conf = src.get("nli_confidence", "")
                        in_db = src.get("in_database", False)
                        
                        # Write clean formatted output
                        log_file.write(f"  {i}. {url}\n")
                        if domain:
                            log_file.write(f"     Domain: {domain} {'✓ (In DB)' if in_db else '✗ (Not in DB)'}\n")
                        if title:
                            log_file.write(f"     Title: {title[:100]}...\n")
                        if snippet:
                            log_file.write(f"     Evidence: {snippet}...\n")
                        if similarity:
                            log_file.write(f"     Similarity: {similarity}\n")
                        if nli_label:
                            log_file.write(f"     NLI: {nli_label} (confidence: {nli_conf})\n")
                    
                    if len(sources) > 3:
                        log_file.write(f"  ... and {len(sources) - 3} more sources.\n")
                else:
                    log_file.write("No evidence sources found.\n")
                log_file.write("="*100 + "\n\n")
        except Exception as log_err:
            print(f"Logging Error: {log_err}")

        return final_response
    
    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------
app.include_router(admin_router)
app.include_router(member_router)

# -------------------------------------------------------------------
# RUN SERVER
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)