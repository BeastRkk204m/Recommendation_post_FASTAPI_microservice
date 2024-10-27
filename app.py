import schema
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from table_post import Post
from table_user import User
from table_feed import Feed
from database import SessionLocal
from sqlalchemy import func

app = FastAPI()

def get_db ():
    with SessionLocal() as db:
        return db

@app.get("/user/{id}", response_model = schema.UserGet)
def get_user_id (id, db = Depends(get_db)) -> schema.UserGet:
    result = db.query(User).where(User.id == id).one_or_none()
    if not result:
        raise HTTPException(404, "user not found")
    else:
        return result

@app.get("/post/{id}", response_model = schema.PostGet)
def get_post_id (id, db = Depends(get_db)) -> schema.PostGet:
    result = db.query(Post).where(Post.id == id).one_or_none()
    if not result:
        raise HTTPException(404, "post not found")
    else:
        return result

@app.get("/user/{id}/feed", response_model = List [schema.FeedGet])
def get_user_feed (id: int, db = Depends(get_db), limit: int = 10):
    result = db.query(Feed).filter(Feed.user_id == id)\
                .order_by(Feed.time.desc())\
                .limit(limit)\
                .all()
    return result

@app.get("/post/{id}/feed", response_model = List [schema.FeedGet])
def get_post_feed (id: int, db = Depends(get_db), limit: int = 10):
    result = db.query(Feed).filter(Feed.post_id == id)\
                .order_by(Feed.time.desc())\
                .limit(limit)\
                .all()
    return result

@app.get("/post/recommendations/", response_model = List [schema.PostGet])
def get_recommended_feed (id: int, db = Depends(get_db), limit: int = 10):
    result = db.query(Post)\
            .select_from(Feed)\
            .filter(Feed.action == 'like')\
            .join(Post)\
            .group_by(Post.id)\
            .order_by(func.count(Post.id).desc())\
            .limit(limit)\
            .all()
    return result