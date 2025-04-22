from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import  ExpiredSignatureError, jwt, JWTError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from datetime import  time, timedelta, datetime
from auth.schemas import CreateUser
from auth.model import Follow, UserModel

from dotenv import load_dotenv
import os

load_dotenv()

from database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


SECRETE_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def existingUser(db: Session, username: str, email: str):
    return db.query(UserModel).filter((UserModel.username == username)| (UserModel.email == email)).first()


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRETE_KEY, algorithm=ALGORITHM)
    return encode_jwt

async def refreshToken(refresh_token):
    try:
        payload = jwt.decode(refresh_token, SECRETE_KEY, algorithms=[ALGORITHM])
        # (Optional) Check if the refresh token matches the one stored in the database
        new_access_token_payload = {
            "userID": payload["userID"],
            "exp": time.time() + 600 * 10  # New access token expires in 60 minutes
        }
        new_access_token = jwt.encode(new_access_token_payload, SECRETE_KEY, algorithm=ALGORITHM)
        return {"access_token": new_access_token}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired.")
    
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> bool:
        try:
            jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM]) 
            return True
        except JWTError:
           return False
       
    def extract_user_id(self, token: str) -> int:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM]) 
        return payload.get("user_id")

def get_current_user(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Query the database for the user
        user = db.query(UserModel).filter(UserModel.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_user_by_id(db: Session, id: int):
    return db.query(UserModel).filter(UserModel.id == id).first()


def create_user(db: Session, user: CreateUser):
    try:    
        newUser = UserModel(
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            hash_passwd=pwd_context.hash(user.hash_passwd),
            dob=user.dob,
            profile_pic=user.profile_pic or None,
            gender=user.gender.upper(),
            bio=user.bio or None)
        db.add(newUser)
        db.commit()
        db.refresh(newUser)
        return newUser
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        raise



def authenticate(db: Session, username: str, password: str):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if not db_user or not pwd_context.verify(password, db_user.hash_passwd):
        return None
    return db_user

    

def follow_user(current_user: UserModel, following_user_id: int, db: Session):
    following_user = get_user_by_id(db, following_user_id)
    user_id = current_user.id
    if not current_user or not following_user:
        return None  # If either user is missing, return None
       
    # Check if the user is already following
    existing_follow = db.query(Follow).filter_by(follower_id=user_id, following_id=following_user_id).first()
    if existing_follow:
        return {"message": "Already following this user"}

    # Create a new Follow entry
    follow_entry = Follow(follower_id=user_id, following_id=following_user_id)
    db.add(follow_entry)

    # Update follower and following counts
    current_user.following_count += 1
    following_user.follower_count += 1

    db.commit()
    return {"message": "Followed user successfully"}


def unfollow_user(current_user:UserModel,following_user_id:int,db:Session):
    user_id = current_user.id
    following_user = get_user_by_id(db,following_user_id)
    if not current_user or not following_user:
        return None
    existing_follow = db.query(Follow).filter_by(follower_id=user_id, following_id=following_user_id).first()
    if not existing_follow:
        return {"message": "you're not following this user"}
    
    current_user.following_count -= 1
    following_user.follower_count -= 1

    db.commit()
    return {"message": "UnFollowed user successfully"}