from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .m_schema import UserCreate, UserResponse, VoteRequest, VoteResponse , VoteSourceRequest ,VoteSourceResponse
from .member_controller import MemberController
from database import get_db
from pydantic import BaseModel
from models import Tweet , VerificationStatus , Vote , VerificationResult , VoteSource , User, UserSocialLink
from typing import Dict ,List
import sys
from sqlalchemy import func ,exc, select , text , case
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="/member",
    tags=["member"]
)

class VoteOverTimeResponse(BaseModel):
    date: str
    votes: int
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str
    


# In your schemas.py
class ContributionsResponse(BaseModel):
    total_votes: int
    total_sources: int
    username: str
    current_streak: int  # ✅ Make sure this field exists
    
    class Config:
        from_attributes = True
    



class MemberActivityResponse(BaseModel):
    id: int
    postContent: str
    userVote: str
    addedSources: List[str]

    class Config:
        from_attributes = True




#-------------------------------------------------
















class VotingSystem:
    @staticmethod
    def calculate_vote_percentage_and_verdict(db: Session, tweet_id: int):
        """
        Calculate voting percentage and determine verdict based on rules
        """
        # Count total votes and true votes
        vote_stats = db.query(
            func.count(Vote.vote_id).label('total_votes'),
            func.sum(case((Vote.vote == True, 1), else_=0)).label('true_votes')
        ).filter(Vote.tweet_id == tweet_id).first()
        
        total_votes = vote_stats.total_votes or 0
        true_votes = vote_stats.true_votes or 0
        
        # Calculate percentage in favor
        if total_votes > 0:
            votes_in_favor_percentage = (true_votes / total_votes) * 100
        else:
            votes_in_favor_percentage = Decimal('0.00')
        
        # Determine verdict based on rules
        verdict = VotingSystem.determine_verdict(total_votes, votes_in_favor_percentage)
        
        return {
            'total_votes': total_votes,
            'true_votes': true_votes,
            'false_votes': total_votes - true_votes,
            'votes_in_favor_percentage': votes_in_favor_percentage,
            'verdict': verdict
        }
    
    @staticmethod
    def determine_verdict(total_votes: int, percentage: Decimal) -> str:
        """
        Determine verdict based on voting rules
        """
        if total_votes < 4:
            return "Unverified"
        elif percentage >= Decimal('65'):
            return "TRUE"
        elif (100 - percentage) >= Decimal('65'):  # False votes >= 65%
            return "FALSE"
        
    
    @staticmethod
    def update_verification_result(db: Session, tweet_id: int):
        """
        Update VerificationResult table with voting results
        """
        # Calculate voting statistics
        vote_data = VotingSystem.calculate_vote_percentage_and_verdict(db, tweet_id)
        
        # Find or create verification result
        verification_result = db.query(VerificationResult).filter(
            VerificationResult.tweet_id == tweet_id
        ).first()
        
        if not verification_result:
            verification_result = VerificationResult(
                tweet_id=tweet_id,
                status="pending"
            )
            db.add(verification_result)
        
        # Update verification result with voting data
        verification_result.votes_in_favor_percentage = vote_data['votes_in_favor_percentage']
        verification_result.verdict = vote_data['verdict']
        
        # Update status based on verdict
        if vote_data['verdict'] in ["TRUE", "FALSE"]:
            verification_result.status = "verified"
            
        
        else:  # PENDING
            verification_result.status = "pending"
        
        # Also update the tweet's verification status
        tweet = db.query(Tweet).filter(Tweet.tweet_id == tweet_id).first()
        if tweet:
            if vote_data['verdict'] in ["TRUE", "FALSE"]:
                tweet.verification_status = VerificationStatus.verified
            else:
                tweet.verification_status = VerificationStatus.pending
        
        db.commit()
        
        return vote_data













#-------------------------------------------------------





@router.get("/accuracy/{member_id}")
async def get_member_accuracy(member_id: int, db: Session = Depends(get_db)):
    try:
        # SQL query using your exact query
        query = text("""
            SELECT 
                u.user_id,
                u.username,
                COUNT(v.vote_id) as total_votes,
                SUM(CASE WHEN v.vote = true THEN 1 ELSE 0 END) as true_votes,
                SUM(CASE WHEN v.vote = false THEN 1 ELSE 0 END) as false_votes,
                SUM(CASE 
                    WHEN (v.vote = true AND vr.verdict ILIKE '%true%') THEN 1 
                    ELSE 0 
                END) as correct_true_votes,
                SUM(CASE 
                    WHEN (v.vote = false AND vr.verdict ILIKE '%false%') THEN 1 
                    ELSE 0 
                END) as correct_false_votes,
                SUM(CASE 
                    WHEN (v.vote = true AND vr.verdict ILIKE '%true%') OR 
                         (v.vote = false AND vr.verdict ILIKE '%false%') THEN 1 
                    ELSE 0 
                END) as total_correct_votes,
                ROUND(
                    (SUM(CASE 
                        WHEN (v.vote = true AND vr.verdict ILIKE '%true%') OR 
                             (v.vote = false AND vr.verdict ILIKE '%false%') THEN 1 
                        ELSE 0 
                    END) * 100.0 / NULLIF(COUNT(v.vote_id), 0)), 2
                ) as accuracy_percentage
            FROM votes v
            INNER JOIN users u ON u.user_id = v.user_id
            INNER JOIN verification_results vr ON vr.tweet_id = v.tweet_id
            WHERE v.user_id = :member_id
            GROUP BY u.user_id, u.username
        """)
        
        # Execute the query
        result = db.execute(query, {"member_id": member_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Member not found or no votes recorded")
        
        # Convert result to dictionary - match the frontend expectation
        accuracy_data = {
            "accuracy": float(result.accuracy_percentage) if result.accuracy_percentage else 0.0
        }
        
        return accuracy_data
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching accuracy data for member {member_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")







@router.get("/profile/{user_id}")
async def get_member_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Get profile information for a member using exact SQL query translation
    """
    try:
        # SQLAlchemy equivalent of your SQL query
        stmt = select(
            User.user_id,
            User.username,
            User.email,
            User.city,
            User.occupation,
            UserSocialLink.platform.label("social_platform"),
            UserSocialLink.url.label("social_url")
        ).select_from(User)\
         .outerjoin(UserSocialLink, User.user_id == UserSocialLink.user_id)\
         .where(User.user_id == user_id)

        # Execute the query
        result = db.execute(stmt).first()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        # Convert result to dictionary
        profile_data = {
            "user_id": result.user_id,
            "username": result.username,
            "email": result.email,
            "city": result.city,
            "occupation": result.occupation,
            "socialPlatform": result.social_platform,  # Matches your React frontend
            "socialUrl": result.social_url  # Matches your React frontend
        }

        return profile_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")
        
        
















@router.get("/activity/{member_id}")
def get_member_activity(member_id: int, db: Session = Depends(get_db)):
    try:
        # SQLAlchemy query equivalent of your SQL query
        results = db.query(
            Tweet.tweet_id,
            Tweet.tweet_text,
            Vote.vote,
            VoteSource.source_url
        ).select_from(Vote)\
         .join(Tweet, Vote.tweet_id == Tweet.tweet_id)\
         .outerjoin(VoteSource, Vote.vote_id == VoteSource.vote_id)\
         .filter(Vote.user_id == member_id)\
         .order_by(Vote.voted_at.desc())\
         .all()

        # Transform the results into the expected format
        activity_map = {}
        
        for tweet_id, tweet_text, vote, source_url in results:
            if tweet_id not in activity_map:
                activity_map[tweet_id] = {
                    "id": tweet_id,
                    "postContent": tweet_text,
                    "userVote": "True" if vote else "False",  # Assuming vote is boolean
                    "addedSources": []
                }
            
            # Add source URL if it exists
            if source_url:
                activity_map[tweet_id]["addedSources"].append(source_url)

        # Convert map to list and return
        activity_data = list(activity_map.values())
        
        return activity_data

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving activity: {e}")











    
@router.post("/vote_sources", response_model=VoteSourceResponse)
async def add_vote_source(
    vote_data: VoteSourceRequest,
    db: Session = Depends(get_db)
):
    try:
        return MemberController.create_vote_source(vote_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving source: {str(e)}")
    
    













# Request model

@router.post("/vote", response_model=VoteResponse)
async def create_vote(
    vote_data: VoteRequest, 
    db: Session = Depends(get_db)
):
    vote_id = await MemberController.create_vote(db, vote_data)

    tweets_with_votes = db.query(Vote.tweet_id).distinct().all()
        
    results = []
    for tweet in tweets_with_votes:
        tweet_id = tweet[0]
        vote_data = VotingSystem.update_verification_result(db, tweet_id)
        results.append({
                "tweet_id": tweet_id,
                **vote_data
            })
    return {"vote_id": vote_id}




# In your FastAPI endpoint file
@router.get("/contributions/{member_id}", response_model=ContributionsResponse)
async def get_member_contributions(
    member_id: int,
    db: Session = Depends(get_db)
):
    """
    Get member's total votes and sources contributed
    """
    try:
        # FIX: Remove 'await' here because get_contributions is now synchronous
        return MemberController.get_contributions(db, member_id)
    except Exception as e:
        logger.error(f"Error in get_member_contributions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching contribution data: {str(e)}"
        )

@router.post("/login")
def login_member(data: LoginRequest, db: Session = Depends(get_db)):
    return MemberController.login_member(data.email, data.password, db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_member(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return MemberController.register_member(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )
        
        


@router.get("/tweets/{user_id}")
def get_all_tweets_for_members(user_id: int, db: Session = Depends(get_db)):
    try:
        # SQLAlchemy query equivalent of your SQL query
        tweets = db.query(Tweet).join(
            VerificationResult, Tweet.tweet_id == VerificationResult.tweet_id
        ).filter(
            VerificationResult.verdict == 'Unverified',
            ~Tweet.tweet_id.in_(
                db.query(Vote.tweet_id).filter(Vote.user_id == user_id).subquery()
            )
        ).order_by(Tweet.submit_date.desc()).all()

        return [
            {
                "tweet_id": tweet.tweet_id,
                "user_id": tweet.user_id,
                "content": tweet.tweet_text,
                "submit_date": tweet.submit_date.isoformat()
            }
            for tweet in tweets
        ]

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving tweets: {e}")
    



@router.get("/votes-over-time/{member_id}", response_model=List[VoteOverTimeResponse])
async def get_votes_over_time(
    member_id: int,
    days: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get member's votes over the last N days
    """
    try:
        return await MemberController.get_votes_over_time(db, member_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching vote data: {str(e)}"
        )
    









