#schemas.py
from pydantic import BaseModel ,HttpUrl
from datetime import datetime

# --- Tweet Schemas ---
from typing import Optional


# Base schema for a tweet's properties
class TweetBase(BaseModel):
    tweet_text: str

# Schema for creating a new tweet (used in request body)
class TweetCreate(TweetBase):
    pass

# Schema for representing a tweet in an API response
class Tweet(TweetBase):
    tweet_id: int
    verification_status: str  # Pydantic will convert the Enum to a string
    submit_date: datetime

    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models
        


class AccountCreate(BaseModel):
    name: str
    platform: str
    url: HttpUrl
    category: str
    admin_id: int
    
class SummaryStat(BaseModel):
    title: str
    value: int
    icon: str
    color: str
    bgColor: str

class SourceDistribution(BaseModel):
    name: str
    value: int

class RecentActivityItem(BaseModel):
    title: str
    count: int
    icon: str
    color: str
    
    
    # It matches the payload sent by your React app.
class PlatformAccountCreate(BaseModel):
    name: str
    platform: str
    url: HttpUrl  # Using HttpUrl provides automatic URL validation
    category: str
    admin_id: int

# This schema is used for the response model.
# It includes all the data from creation plus the new `account_id`.
class PlatformAccount(PlatformAccountCreate):
    account_id: int

    class Config:
        # This allows the Pydantic model to be created from an ORM object
        # (the SQLAlchemy model instance you'll return from the database).
        from_attributes = True # Re
    
    
