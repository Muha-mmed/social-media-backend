from fastapi import APIRouter, Depends, HTTPException, Query
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from auth.model import UserModel

from .schemas import CreateUser, UserResponse
from .service import (create_access_token, create_user, existingUser, authenticate,JWTBearer, follow_user,get_current_user,get_user_by_id,refreshToken, unfollow_user)
from database import get_db,Base,engine

Base.metadata.create_all(bind=engine)


auth_router = APIRouter(tags=["auth"],prefix="/auth")

@auth_router.post("/signup", status_code=201)
async def signup(user: CreateUser, db: Session = Depends(get_db)):
    # Check if username or email already exists
    db_user = existingUser(db, user.username, user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email or Username already exists")
    
    # Create new user
    create_user(db, user)
    
    # Generate access token
    access_token = await create_access_token({"sub": user.username})
    
    return {
        "message": "User created successfully",
        "access_token": access_token
    }

@auth_router.post("/login")
async def login(username:str,password:str,db: Session = Depends(get_db)):
    # Authenticate user
    db_user = authenticate(db, username, password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Generate access token
    access_token = await create_access_token({"sub":username})
    
    return {
        "token": access_token,
        "token_type": "bearer"
    }
    
@auth_router.post("/refresh")
async def refresh_token(refresh_token: str):
    refresh = await refreshToken(refresh_token)
    return {
        "refresh token": refresh,
        "token_type": "bearer"
    }

@auth_router.get("/", dependencies=[Depends(JWTBearer())])
async def home(username: str = Query(...), db: Session = Depends(get_db)):
    user_list = db.query(UserModel).filter(UserModel.username == username).first()
    return user_list
   
@auth_router.get('/profile', response_model=UserResponse, dependencies=[Depends(JWTBearer())])
async def profile(db_user: UserResponse = Depends(get_current_user)):
    return db_user

@auth_router.get('/user{user_id}', dependencies=[Depends(JWTBearer())])
async def user(user_id: int,db:Session=Depends(get_db)):
    user = get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(status_code=404,detail="user not found")
    return user

    
@auth_router.post('/follow',dependencies=[Depends(JWTBearer())])
async def follow(following_id: int,user_id: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if following_id == user_id.id :
        raise HTTPException(status_code=404, detail="User can not follow themselves")
    
    result = follow_user(user_id, following_id, db)

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result

@auth_router.post('/unfollow',dependencies=[Depends(JWTBearer())])
async def follow(following_id: int,user_id: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if following_id == user_id.id :
        raise HTTPException(status_code=404, detail="User can not unfollow themselves")
    
    result = unfollow_user(user_id, following_id, db)

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result