from pydantic import BaseModel, EmailStr , HttpUrl
from typing import Optional , List

class SocialLinkCreate(BaseModel):
    platform: str
    url: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    city: Optional[str] = None
    occupation: Optional[str] = None
    social_platform: Optional[str] = None  # Match frontend field name
    social_url: Optional[str] = None       # Match frontend field name

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    approval_status: str
    
    class Config:
        orm_mode = True
        
        
class VoteRequest(BaseModel):
    tweet_id: int
    user_id: int
    vote: bool

class VoteResponse(BaseModel):
    vote_id: int
    
    
class VoteSourceRequest(BaseModel):
    vote_id: int
    source_url: str  # Ensures it's a valid URL

class VoteSourceResponse(BaseModel):
    source_id: int
    vote_id: int
    source_url: HttpUrl

    class Config:
        orm_mode = True


class MemberActivityResponse(BaseModel):
    id: int
    postContent: str
    userVote: str
    addedSources: List[str]

    class Config:
        from_attributes = True