from database import Base 
from sqlalchemy import Column,String,text,Integer,Boolean,TIMESTAMP,ForeignKey,Table
from sqlalchemy.orm import relationship


post_hashtags = Table(
    "post_hashtags",
    Base.metadata,
    Column("post_ids", Integer,ForeignKey("posts.id")),
    Column("hashtag_id", Integer,ForeignKey("hashtag.id"))
)

post_likes = Table(
    "post_likes",
    Base.metadata,
    Column("user_id",Integer,ForeignKey("users.id")),
    Column("post_id", Integer,ForeignKey("posts.id"))
)

class PostModel(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    content = Column(String,nullable=True)
    images = Column(String,nullable=True)
    publish= Column(Boolean,default=False)
    likes_count = Column(Integer,default=0)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('Now()'))
    
    author_id = Column(Integer,ForeignKey("users.id"))
    
    liked_by_users = relationship("auth.model.UserModel",secondary=post_likes,back_populates="liked_posts")
    author = relationship("auth.model.UserModel",back_populates="posts")    
    hashtag = relationship("Hashtag",secondary=post_hashtags,back_populates="posts")
    
class Hashtag(Base):
    __tablename__ = 'hashtag'
    
    id = Column(Integer,primary_key=True,index=True)
    content = Column(String,index=True)
    
    posts = relationship("PostModel",secondary=post_hashtags,back_populates="hashtag")