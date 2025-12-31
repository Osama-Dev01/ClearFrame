# admin_routes.py
from fastapi import APIRouter, Depends, HTTPException ,Request , status
from sqlalchemy.orm import Session 
from pydantic import BaseModel
from database import get_db
from .admin_controller import AdminController
from schemas import AccountCreate , PlatformAccountCreate 
from models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

class AccountCreate(BaseModel):
    category: str
    name: str
    platform: str
    url: str

class AccountUpdate(BaseModel):
    category: str = None
    name: str = None
    platform: str = None
    url: str = None

class ApprovalUpdate(BaseModel):
    approve: bool


class TopMemberResponse(BaseModel):
    name: str
    votes: int
  


@router.get("/tweetdata")
async def get_tweet_verification_stats(db: Session = Depends(get_db)):
    """
    Endpoint to get tweet verification statistics.
    Returns counts for verified (true), unverified (false), and pending (unverified).
    """
    try:
        stats = AdminController.get_tweet_verification_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))













@router.delete("/delmembers/{member_id}", status_code=status.HTTP_200_OK)
def del_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a member by user_id (Admin action)
    """
    return AdminController.del_member(member_id , db)


























@router.get("/top-members")
async def get_top_members(db: Session = Depends(get_db)):
    """
    Endpoint to get top 5 members by votes.
    """
    try:
        members = AdminController.get_top_members(db)
        return members
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





# Routes
@router.post("/login")
def admin_login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return AdminController.login(db, credentials.username, credentials.password)

@router.post("/platform_accounts", status_code=201)
def create_platform_account(account: PlatformAccountCreate, db: Session = Depends(get_db)):
    return AdminController.create_platform_account(db, account)

@router.get("/numbers")
def get_admin_dashboard(db: Session = Depends(get_db)):
    return AdminController.get_dashboard_stats(db)


@router.get("/approved-members")  # Changed from pending-members to approved-members
def get_approved_members(db: Session = Depends(get_db)):
    return AdminController.get_approved_members(db)




@router.delete("/member_to_delete/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db)
   
):
    return AdminController.delete_member(db, member_id)



@router.post("/accept_member/{member_id}")
def accept_member(
    member_id: int,
    db: Session = Depends(get_db),
    
):
    return AdminController.accept_member(db, member_id)

@router.post("/decline_member/{member_id}")
def decline_member(
    member_id: int,
    db: Session = Depends(get_db),
  
):
    return AdminController.decline_member(db, member_id)


@router.get("/approval_requests")
def get_approval_requests(
    db: Session = Depends(get_db),
   
):
   
    return AdminController.get_pending_approvals(db)



@router.get("/search")
def search_accounts(
    search_term: str,
    db: Session = Depends(get_db)
):
    return AdminController.search_accounts_by_name(db, search_term)




@router.post("/accounts", status_code=201)
async def create_account(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()

        # Manual field validation (you can make this more robust)
        required_fields = ["name", "platform", "url", "category", "admin_id"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=422, detail=f"Missing field: {field}")

        # Optional: Basic URL validation
        if not data["url"].startswith("http://") and not data["url"].startswith("https://"):
            raise HTTPException(status_code=422, detail="Invalid URL format")

        return AdminController.create_account(data, db)

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Account creation failed")




@router.get("/pending-members")
def get_pending_members(db: Session = Depends(get_db)):
    return AdminController.get_pending_members(db)

@router.put("/approve-member/{member_id}")
def approve_member(
    member_id: int, 
    decision: ApprovalUpdate, 
    db: Session = Depends(get_db)
):
    return AdminController.update_member_approval(db, member_id, decision.approve)

@router.post("/platform-accounts")
def create_platform_account(
    account: AccountCreate, 
    current_admin: dict = Depends(admin_login),  # Get admin from login
    db: Session = Depends(get_db)
):
    return AdminController.create_platform_account(db, account.dict(), current_admin.user_id)

@router.get("/platform-accounts")
def get_platform_accounts(db: Session = Depends(get_db)):
    return AdminController.get_platform_accounts(db)

@router.put("/platform-accounts/{account_id}")
def update_platform_account(
    account_id: int, 
    update_data: AccountUpdate, 
    db: Session = Depends(get_db)
):
    return AdminController.update_platform_account(db, account_id, update_data.dict(exclude_unset=True))

@router.delete("/platform-accounts/{account_id}")
def delete_platform_account(account_id: int, db: Session = Depends(get_db)):
    return AdminController.delete_platform_account(db, account_id)

@router.get("/members")
def get_all_members(db: Session = Depends(get_db)):
    return AdminController.get_members(db)

@router.get("/members/{member_id}")
def get_member_profile(member_id: int, db: Session = Depends(get_db)):
    return AdminController.get_member_profile(db, member_id)

@router.delete("/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    return AdminController.delete_member(db, member_id)





