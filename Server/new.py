from simhash import TweetMatchingSystem
from database import engine, get_db, SessionLocal, Base
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from urllib.parse import urlparse
from models import (
    User,
    ApprovalStatus,
    VerificationResult,
    VerificationSource,
    Tweet,
    VerificationStatus
)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="TweetPlug Verification Backend", version="2.1")

# CORRECTED: Create session directly without Depends
db = SessionLocal()  # Create actual database session
try:
    # Initialize system
    matching_system = TweetMatchingSystem(db_session=db)
    matching_system.initialize()  # Loads from helper.txt or processes DB
    
    # Test matching
    results = matching_system.match_tweet("BREAKING: Chinese scientists developing a drug to extend human life to 150 years NYT The breakthrough hinges on a grapeseed compound, PCC1, which in tests destroyed aged cells in mice, extending their lifespan by over 9% This 'holy grail' technology is now being adapted for humans.")
    print(f"Matching results: {results}")
    
except Exception as e:
    print(f"Error during initialization: {e}")
    raise
finally:
    db.close()  # Always close the session


# Start with: uvicorn filename:app --reload