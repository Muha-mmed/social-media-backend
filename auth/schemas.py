import datetime
from typing import Optional
from pydantic import BaseModel,EmailStr
from datetime import date,datetime

from auth.enum import GENDER

class CreateUser(BaseModel):
    full_name : str
    username : str
    dob : date
    gender :  GENDER 
    profile_pic : Optional[str] = None
    bio : Optional[str]= None
    email : EmailStr   
    hash_passwd : str
    
    
    class Config:
        use_enum_values = True

    
class UpdateUser(BaseModel):
    full_name : Optional[str]
    username : Optional[str]
    email : Optional[str]     
    dob : Optional[date] 
    gender :  Optional[GENDER]
    profile_pic : Optional[str]
    bio : Optional[str]
    
class UserResponse(BaseModel):
    id : int
    full_name : str
    username : str
    dob : Optional[date] = None
    gender :  str = None
    profile_pic :str = None
    bio : str= None
    email : str 
    created_at : datetime
    
    class Config:
        from_attributes = True 
