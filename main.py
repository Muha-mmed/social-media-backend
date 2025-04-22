from fastapi import FastAPI
from auth.routes import auth_router
from post.routes import post_router


app= FastAPI()

app.include_router(auth_router)
app.include_router(post_router)