from fastapi import APIRouter, Depends,HTTPException
from auth.model import UserModel
from database import get_db,Base,engine
from .post_services import createPost,get_all_post,get_user_posts,get_feed_post,delete_post,get_post_by_id,get_post_by_hashtag, like_post, unlike_post
from sqlalchemy.orm import Session
from .schemas import CreatePost
from auth.service import JWTBearer, get_current_user
from auth.service import get_user_by_id


post_router = APIRouter(tags=["post"],prefix = "/post")

Base.metadata.create_all(bind=engine)


@post_router.get("/",dependencies=[Depends(JWTBearer())])
def feed(db:Session = Depends(get_db)):
    return get_feed_post(db)

@post_router.post("/create", dependencies=[Depends(JWTBearer())])
async def create_post(post: CreatePost, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    newPost = createPost(db, post, current_user)
    if not newPost:
        raise HTTPException(status_code=401, detail="invalid user ID")
    return {"status": "success", "data": newPost}
    
@post_router.get("/posts", dependencies=[Depends(JWTBearer())])
def all_post(db:Session = Depends(get_db)):
    return get_all_post(db)

@post_router.get("/user_post",dependencies=[Depends(JWTBearer())])
def user_post(user_id:int, db:Session = Depends(get_db)):
    return get_user_posts(db,user_id)

@post_router.delete("/delete", dependencies=[Depends(JWTBearer())])
def delete_Post_route(post_id: int, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    response = delete_post(db, current_user, post_id)      

    if response["message"] == "Post not found":
        raise HTTPException(status_code=404, detail="Post not found")
    elif response["message"] == "You are not authorized to delete this post":
        raise HTTPException(status_code=403, detail="You are not authorized to delete this post")
    
    return response
    
    
@post_router.get("/postbyhashtag", dependencies=[Depends(JWTBearer())])
def get_post_by_hashtags(hashtag:str,db:Session=Depends(get_db)):
    posts = get_post_by_hashtag(db,hashtag)
    if not posts:
        return {"message":"No post which this hashtag"}
    return posts


# ✅ Updated route
@post_router.post("/like", dependencies=[Depends(JWTBearer())])
def user_like_post(post_id: int, username: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    result = like_post(db, post_id, username)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found or user doesn't exist")
    return result

@post_router.post("/unlike", dependencies=[Depends(JWTBearer())])
def user_like_post(post_id: int, username: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    result = unlike_post(db, post_id, username)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found or user doesn't exist")
    return result

