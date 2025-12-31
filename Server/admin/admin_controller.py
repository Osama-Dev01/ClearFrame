# admin_controller.py
from sqlalchemy.orm import Session
from models import User, PlatformAccount, ApprovalStatus

from fastapi import HTTPException , status
from sqlalchemy import func , text



class AdminController:



   
   
    @staticmethod
    def del_member(member_id: int, db: Session):
        user = db.query(User).filter(User.user_id == member_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # Optional: prevent rejecting admins
        if user.role.name.lower() == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin cannot be rejected"
            )

        try:
            user.approval_status = ApprovalStatus.rejected
           
            db.commit()

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

        return {
            "message": "Member approval status changed to rejected",
            "user_id": member_id,
            "approval_status": "rejected"
        }
















   








    @staticmethod
    def get_tweet_verification_stats(db: Session):
        """
        Counts unique tweets by normalized verdict (true, false, unverified).
        """
        try:
            query = text("""
                SELECT 
                    CASE 
                        WHEN LOWER(verdict) = 'true' THEN 'true'
                        WHEN LOWER(verdict) = 'false' THEN 'false'
                        ELSE 'unverified'
                    END AS verdict,
                    COUNT(DISTINCT tweet_id) AS count
                FROM verification_results
                GROUP BY 
                    CASE 
                        WHEN LOWER(verdict) = 'true' THEN 'true'
                        WHEN LOWER(verdict) = 'false' THEN 'false'
                        ELSE 'unverified'
                    END;
            """)

            result = db.execute(query).fetchall()

            # Default counts
            counts = {
                'true': 0,
                'false': 0,
                'unverified': 0
            }

            # Fill in counts from the query result
            for row in result:
                verdict = row.verdict.lower()  # normalize
                if verdict in counts:
                    counts[verdict] = row.count

            return [
                {"name": "Verified", "value": counts['true']},
                {"name": "False", "value": counts['false']},
                {"name": "Unverified", "value": counts['unverified']}
            ]

        except Exception as e:
            print("Error fetching tweet verification stats:", e)
            raise e




















    @staticmethod
    def get_top_members(db: Session):
        """
        Fetch top 5 approved active members by total votes.
        """
        try:
            query = text("""
                SELECT 
                    u.username AS name,
                    COUNT(v.vote_id) AS votes
                FROM users u
                JOIN votes v ON u.user_id = v.user_id
                WHERE u.role = 'member' 
                    AND u.approval_status = 'approved'
                    AND u.is_active = true
                GROUP BY u.user_id, u.username, u.profile_picture_url
                ORDER BY votes DESC
                LIMIT 1;
            """)

            result = db.execute(query).fetchall()

            # Convert SQLAlchemy Row objects into dicts
            members = [{"name": row.name, "votes": row.votes} for row in result]
            return members

        except Exception as e:
            print("Error fetching top members:", e)
            raise e





    
    
    
    @staticmethod
    def get_dashboard_stats(db: Session):
        try:
            total_users = db.query(func.count(User.user_id)).scalar()
            approved_members = db.query(func.count(User.user_id)).filter(User.approval_status == 'approved').scalar()
            pending_requests = db.query(func.count(User.user_id)).filter(User.approval_status == 'pending').scalar()
            trusted_sources = db.query(func.count(PlatformAccount.account_id)).scalar()

            return {
                "total_users": total_users,
                "approved_members": approved_members,
                "pending_requests": pending_requests,
                "trusted_sources": trusted_sources
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Dashboard data fetch failed: {str(e)}")
    
    
    
    
            
         
         
         
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    @staticmethod
    def login(db: Session, username: str, password: str):
        user = db.query(User).filter(
            User.username == username,
            User.role == 'admin'
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user.password != password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return user
    

            
    @staticmethod
    def delete_member(db: Session, member_id: int):
        # Find the member
        member = db.query(User).filter(
            User.user_id == member_id,
            User.role == 'member'  # Only allow deleting members, not admins
        ).first()
    
        if not member:
            raise HTTPException(
                status_code=404,
                detail="Member not found or not authorized to delete"
            )
    
        try:
            # Delete the member
            db.delete(member)
            db.commit()
            return {"message": "Member deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting member: {str(e)}"
            )



    @staticmethod
    def accept_member(db: Session, member_id: int):
        member = db.query(User).filter(
            User.user_id == member_id,
            User.role == 'member'  # Only process members, not admins
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail="Member not found"
            )
        
        try:
            member.approval_status = 'approved'
            member.is_active = True
            db.commit()
            return {"message": "Member approved successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error approving member: {str(e)}"
            )

    @staticmethod
    def decline_member(db: Session, member_id: int):
        member = db.query(User).filter(
            User.user_id == member_id,
            User.role == 'member'  # Only process members, not admins
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail="Member not found"
            )
        
        try:
            member.approval_status = 'rejected'
            member.is_active = False  # Optional: deactivate rejected members
            db.commit()
            return {"message": "Member declined successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error declining member: {str(e)}"
            )



    @staticmethod
    def get_pending_approvals(db: Session):
        try:
            # Query all members with pending approval
            pending_members = db.query(User).filter(
                User.role == 'member',
                User.approval_status == 'pending'
            ).all()

            return [
                {
                    "user_id": member.user_id,
                    "username": member.username,
                    "email": member.email,
                    "role": member.role,
                    "city": member.city,
                    "occupation": member.occupation,
                    "social_links": [
                        {
                            "platform": link.platform,
                            "url": link.url
                        }
                        for link in member.social_links
                    ] if hasattr(member, 'social_links') else [],
                    "created_at": member.created_at.isoformat() if hasattr(member, 'created_at') and member.created_at else None
                }
                for member in pending_members
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching pending approvals: {str(e)}"
            )






    
    @staticmethod
    def search_accounts_by_name(db: Session, search_term: str):
        results = db.query(PlatformAccount).filter(
            PlatformAccount.name.ilike(f"%{search_term}%")
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail="No matching accounts found")
        

        return results







  
    @staticmethod
    def create_account(account_data: dict, db: Session):
        new_account = PlatformAccount(
            name=account_data["name"],
            platform=account_data["platform"],
            url=account_data["url"],
            category=account_data["category"],
            admin_id=account_data["admin_id"]
        )
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        return new_account










    @staticmethod
    def get_pending_members(db: Session):
        return db.query(User).filter(
            User.role == 'member',
            User.approval_status == ApprovalStatus.pending.value
        ).all()

    @staticmethod
    def update_member_approval(db: Session, member_id: int, approve: bool):
        member = db.query(User).filter(
            User.user_id == member_id,
            User.role == 'member'
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        member.approval_status = ApprovalStatus.approved.value if approve else ApprovalStatus.rejected.value
        db.commit()
        return member

    @staticmethod
    def create_platform_account(db: Session, account_data: dict, admin_id: int):
        account = PlatformAccount(
            category=account_data['category'],
            name=account_data['name'],
            platform=account_data['platform'],
            url=account_data['url'],
            admin_id=admin_id
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    
    
    @staticmethod
    def get_approved_members(db: Session):
        # First get all approved members
        approved_members = db.query(User).filter(
            User.role == 'member',
            User.approval_status == 'approved'
        ).all()

        member_data = []

        # SQL query reused for each member
        stats_query = text("""
            SELECT 
                COUNT(v.vote_id) AS total_votes,
                SUM(
                    CASE 
                        WHEN (v.vote = true AND vr.verdict ILIKE '%true%') OR
                            (v.vote = false AND vr.verdict ILIKE '%false%')
                        THEN 1 ELSE 0
                    END
                ) AS correct_votes,
                ROUND(
                    (SUM(
                        CASE 
                            WHEN (v.vote = true AND vr.verdict ILIKE '%true%') OR
                                (v.vote = false AND vr.verdict ILIKE '%false%')
                            THEN 1 ELSE 0
                        END
                    ) * 100.0) / NULLIF(COUNT(v.vote_id), 0), 2
                ) AS accuracy_percentage
            FROM votes v
            INNER JOIN verification_results vr 
                ON vr.tweet_id = v.tweet_id
            WHERE v.user_id = :member_id
        """)

        # Build response
        for member in approved_members:
            stats = db.execute(stats_query, {"member_id": member.user_id}).fetchone()

            member_data.append({
                "user_id": member.user_id,
                "username": member.username,
                "email": member.email,
                "role": member.role,
                
                "total_votes": stats.total_votes or 0,
                "accuracy_percentage": stats.accuracy_percentage or 0
            })

        return member_data


    @staticmethod
    def get_platform_accounts(db: Session):
        return db.query(PlatformAccount).all()

    @staticmethod
    def update_platform_account(db: Session, account_id: int, update_data: dict):
        account = db.query(PlatformAccount).filter(
            PlatformAccount.account_id == account_id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        for key, value in update_data.items():
            setattr(account, key, value)
        
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete_platform_account(db: Session, account_id: int):
        account = db.query(PlatformAccount).filter(
            PlatformAccount.account_id == account_id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        db.delete(account)
        db.commit()
        return {"message": "Account deleted successfully"}

    @staticmethod
    def get_members(db: Session):
        return db.query(User).filter(User.role == 'member').all()

    @staticmethod
    def get_member_profile(db: Session, member_id: int):
        member = db.query(User).filter(
            User.user_id == member_id,
            User.role == 'member'
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        return member

    @staticmethod
    def delete_member(db: Session, member_id: int):
        member = db.query(User).filter(
            User.user_id == member_id,
            User.role == 'member'
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        db.delete(member)
        db.commit()
        return {"message": "Member deleted successfully"}