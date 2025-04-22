import re
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session
from .model import PostModel,Hashtag,post_hashtags,post_likes
from .schemas import CreatePost,Post
from auth.model import UserModel

# CREATE HASHTAG
def create_hashtags_svc(db:Session,post:PostModel):
  regex = r"#\w+"
  matches = re.findall(regex,post.content)
  
  for match in matches:
    name = match[1:]
    
    hashtag = db.query(Hashtag).filter(Hashtag.content == name).first()
    if not hashtag:
      hashtag = Hashtag(content = name)
      db.add(hashtag)
      db.commit()
    post.hashtag.append(hashtag)

# CREATE POST
def createPost(db: Session, post: CreatePost, current_user: UserModel):
    if current_user.id:
        try:
            newPost = PostModel(
                content=post.content,
                images=post.images,
                publish=post.publish,
                author_id=current_user.id
            )
            db.add(newPost)
            db.commit()
            db.refresh(newPost)
            return newPost
        except Exception as e:
            db.rollback()
            return str(e)
    return None
  
# GET ALL POST IN THE DATABASE
def get_all_post(db:Session) -> list[PostModel]:
  posts = db.query(PostModel).all()
  return posts

def get_user_posts(db:Session,user_id:int) -> list[Post]:
  user_posts = db.query(PostModel).filter(PostModel.author_id == user_id).order_by(desc(PostModel.created_at)).all()
  return user_posts

def get_post_by_hashtag(db:Session,hashtag:str):
  search_hashtag = db.query(Hashtag).filter(Hashtag.content == hashtag).first()
  if not search_hashtag:
    return None
  return search_hashtag.posts

#  GET POST ON FEED
def get_feed_post(db:Session,page:int =1,limit:int=10,hashtag:str=None):
  total_post = db.query(PostModel).count()
  
  offset = (page - 1) * limit
  if offset >= total_post:
    return []
  
  posts = db.query(PostModel,UserModel.username).join(UserModel).order_by(desc(PostModel.created_at))
  
  if hashtag:
    posts = posts.join(post_hashtags).join(Hashtag).filter(Hashtag.content == hashtag)
    
  posts = posts.offset(offset).limit(limit).all()
  
  result = []
  for post,username in posts:
    post_dict = post.__dict__
    post_dict["username"] = username
    result.append(post_dict)
  return result

# GET POST BY ID
def get_post_by_id(db:Session,post_id:int):  
  return db.query(PostModel).filter(PostModel.id == post_id).first()
  

# DELETE POST
def delete_post(db:Session,current_user: UserModel,post_id:int):
  post = get_post_by_id(db, post_id)

  if not post:
    return {"message": "Post not found"}  

  # Ensure user exists in DB
  if current_user.id != post.author_id:
    return {"message": "You are not authorized to delete this post"}
  db.delete(post)    
  db.commit()
  return {"message": "post deleted successfully"}


def like_post(db: Session, post_id: int, user: UserModel):
    post = get_post_by_id(db, post_id)

    if not post:
        return None  # Post not found

    # Ensure user exists in DB
    user_id = db.query(UserModel).filter(UserModel.id == user.id).first()
    if not user_id:
        return None  # User not found

    # Check if user already liked the post
    existing_like = db.execute(
        select(post_likes).where(
            post_likes.c.user_id == user_id.id,
            post_likes.c.post_id == post.id
        )
    ).fetchone()

    if existing_like:
        return {"message": "User already liked this post"}  # Prevent duplicate likes

    # Insert the like into post_likes table
    db.execute(post_likes.insert().values(user_id=user_id.id, post_id=post.id))

    # Increase likes count
    post.likes_count += 1

    db.commit()
    return {"message": "User liked post successfully"}


def unlike_post(db:Session,post_id:int,user:UserModel):
    post = get_post_by_id(db,post_id)
    
    if not post:
      return None
   
    current_user = db.query(UserModel).filter(UserModel.id == user.id).first()
    
    if not current_user:
      return None

    
    existing_like = db.execute(select(post_likes).where(
      post_likes.c.user_id == current_user.id,
      post_likes.c.post_id == post_id
    )).fetchone()
    
    if not existing_like:
      return {"message": "User haven't like this post"} 
          
    db.execute(
        delete(post_likes).where(
            post_likes.c.user_id == current_user.id,
            post_likes.c.post_id == post_id
        )
    )

    # Decrease `likes_count` but ensure it doesn't go negative
    if post.likes_count > 0:
        post.likes_count -= 1
        
    db.commit()
    return {"message": "user unLiked post successfully"}