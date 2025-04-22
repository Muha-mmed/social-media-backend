import datetime
from database import Base
from sqlalchemy import Column, DateTime,String,Date,Integer,ForeignKey,Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .enum import GENDER
from post.model import post_likes

class Follow(Base):
    __tablename__ = 'follow'
    
    follower_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    following_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    
    follower = relationship("UserModel",foreign_keys=[follower_id],back_populates="following")
    following = relationship("UserModel",foreign_keys=[following_id],back_populates="follower")

class UserModel(Base):
    __tablename__ = 'users'
    
    # basic auth
    id= Column(Integer,primary_key=True,index=True)
    full_name = Column(String, nullable=False,index=True)
    username = Column(String, nullable=False,unique=True,index=True)
    email= Column(String, nullable=False,unique=True,index=True)
    hash_passwd = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    
    # profile
    dob =Column(Date)
    gender = Column(SQLAlchemyEnum(GENDER,native_enum=False), nullable=False)
    profile_pic = Column(String)
    bio = Column(String)
    follower_count = Column(Integer,default=0)
    following_count = Column(Integer,default=0)
    
    #other relational DB
    posts = relationship("post.model.PostModel",back_populates="author")
    liked_posts = relationship("post.model.PostModel",secondary=post_likes,back_populates="liked_by_users")
    
    follower = relationship("Follow", foreign_keys=[Follow.following_id],back_populates="following")
    following = relationship("Follow", foreign_keys=[Follow.follower_id],back_populates="follower")