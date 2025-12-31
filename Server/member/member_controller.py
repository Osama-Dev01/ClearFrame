from sqlalchemy.orm import Session 
from models import User, UserSocialLink, UserRole, ApprovalStatus , Vote, VoteSource
from .m_schema import UserCreate
from fastapi import HTTPException
from typing import Dict ,List
from sqlalchemy import func ,exc, select , text
from datetime import datetime , timedelta
from .member_routes import VoteRequest , VoteSourceRequest
from sqlalchemy.exc import IntegrityError
import sys
import logging
#from m_schema import MemberActivityResponse



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemberController:

   
   











    
    @staticmethod
    def register_member(db: Session, user_data: UserCreate):
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        # Create new user with default values
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,  # REMEMBER: Hash this in production!
            city=user_data.city,
            occupation=user_data.occupation,
            role=UserRole.member.value,  # Set default role
            approval_status=ApprovalStatus.pending.value,  # Set default status
            is_active=True  # Set default active status
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Add social link if provided
        if user_data.social_platform and user_data.social_url:
            social_link = UserSocialLink(
                user_id=new_user.user_id,
                platform=user_data.social_platform,
                url=user_data.social_url
            )
            db.add(social_link)
            db.commit()
        
        return new_user
    
    
    @staticmethod
    def login_member(email: str, password: str, db: Session):
        user = db.query(User).filter(User.email == email).first()

        # Check if user exists
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check if password matches
        if user.password != password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check if role is 'member'
        if user.role != UserRole.member:
            raise HTTPException(status_code=403, detail="Only members can log in")

        # Check approval status
        if user.approval_status != ApprovalStatus.approved:
            raise HTTPException(status_code=403, detail="Your account is not approved yet")

        # Optional: Check if account is active
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")

        # Simulate token return (you should replace with real JWT later)
        return {
            "token": f"dummy-token-for-{user.user_id}",
            "id": user.user_id,
           
        }
        
        
    
    @staticmethod
    def get_contributions(db: Session, member_id: int) -> Dict[str, int]:
        """
        Returns a member's total votes, sources contributed, and current streak
        Args:
            db: Database session
            member_id: ID of the member
        Returns:
            Dictionary with total_votes, total_sources, username, and current_streak counts
        """
        # Get total votes count
        total_votes = db.query(func.count(Vote.vote_id))\
                    .filter(Vote.user_id == member_id)\
                    .scalar() or 0
        #logger.info(f"Member ID: {member_id}, Total Votes: {total_votes}")

        # Get total sources count
        total_sources = db.query(func.count(VoteSource.source_id))\
                        .join(Vote, VoteSource.vote_id == Vote.vote_id)\
                        .filter(Vote.user_id == member_id)\
                        .scalar() or 0
        #logger.info(f"Member ID: {member_id}, Total Sources: {total_sources}")
        
        # Get username
        username = db.query(User.username)\
                .filter(User.user_id == member_id)\
                .scalar() or "Unknown"
        #logger.info(f"Member ID: {member_id}, Username: {username}")

        # Add streak calculation
        streak_query = text("""
            WITH daily_votes AS (
                SELECT DISTINCT DATE(voted_at) AS vote_date
                FROM votes 
                WHERE user_id = :user_id
            ),
            ordered_dates AS (
                SELECT 
                    vote_date,
                    ROW_NUMBER() OVER (ORDER BY vote_date DESC) as rn
                FROM daily_votes
            ),
            consecutive_check AS (
                SELECT 
                    vote_date,
                    rn,
                    vote_date + rn * INTERVAL '1 day' AS check_date
                FROM ordered_dates
            )
            SELECT COUNT(*) AS current_streak
            FROM consecutive_check c1
            WHERE EXISTS (
                SELECT 1 FROM consecutive_check c2 
                WHERE c2.vote_date = (SELECT MAX(vote_date) FROM daily_votes) - (c1.rn - 1) * INTERVAL '1 day'
            )
        """)
        
        try:
            #logger.info(f"Calculating streak for member {member_id}")
            result = db.execute(streak_query, {"user_id": member_id})
            current_streak = result.scalar() or 0
            #logger.info(f"Member ID: {member_id}, Current Streak: {current_streak}")
        except Exception as e:
            #logger.error(f"Error calculating streak for member {member_id}: {e}")
            current_streak = 0

        return {
            "total_votes": total_votes,
            "total_sources": total_sources,
            "username": username,
            "current_streak": current_streak
        }
            
         
    @staticmethod
    async def create_vote(db: Session, vote_data: VoteRequest) -> int:
        """
        Create a new vote or return error if already voted.
        """
        new_vote = Vote(
            tweet_id=vote_data.tweet_id,
            user_id=vote_data.user_id,
            vote=vote_data.vote
        )

        try:
            db.add(new_vote)
            db.commit()
            db.refresh(new_vote)
            return new_vote.vote_id

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="User has already voted on this tweet.")

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        
        
        
    @staticmethod
    def create_vote_source(vote_data: VoteSourceRequest, db: Session) -> VoteSource:
        try:
            print(f"Creating VoteSource with vote_id={vote_data.vote_id}, url={vote_data.source_url}")

            new_source = VoteSource(
                vote_id=vote_data.vote_id,
                source_url=vote_data.source_url
            )
            db.add(new_source)
            db.commit()
            db.refresh(new_source)

            return new_source
        except Exception as e:
            print(f"Error in create_vote_source: {e}")
            raise



    @staticmethod
    async def get_votes_over_time(db: Session, member_id: int, days: int = 10) -> List[Dict[str, any]]:
        """
        Get member's votes over the last N days
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            logger.info(f"Fetching votes for member {member_id} from {start_date.date()} to {end_date.date()}")
            
            # Query to get votes grouped by date
            votes_by_date = db.query(
                func.date(Vote.voted_at).label('date'),
                func.count(Vote.vote_id).label('votes')
            ).filter(
                Vote.user_id == member_id,
                func.date(Vote.voted_at) >= start_date.date(),
                func.date(Vote.voted_at) <= end_date.date()
            ).group_by(
                func.date(Vote.voted_at)
            ).order_by(
                func.date(Vote.voted_at)
            ).all()
            
            # Log the raw query results
            logger.info(f"Raw vote data: {[(str(item.date), item.votes) for item in votes_by_date]}")
            
            # Create a complete date range with 0 votes for missing dates
            result = []
            current_date = start_date.date()
            
            for i in range(days):
                date_str = current_date.strftime('%Y-%m-%d')
                display_date = f"Day {i+1}"
                
                # Find votes for this date
                votes_today = next((item.votes for item in votes_by_date 
                                  if item.date == current_date), 0)
                
                result.append({
                    "date": display_date,
                    "votes": votes_today
                })
                
                current_date += timedelta(days=1)
            
            logger.info(f"Processed vote data: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in get_votes_over_time for member {member_id}: {str(e)}")
            raise
