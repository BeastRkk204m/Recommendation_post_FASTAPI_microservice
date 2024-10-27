from pydantic import BaseModel
import datetime



class PostGet(BaseModel):
    id:int
    text:str
    topic:str

    class Config():
        orm_mode = True

class UserGet(BaseModel):
    age:int
    city:str
    country:str
    exp_group:int
    gender:int
    id:int
    os:str
    source:str

    class Config():
        orm_mode = True

class FeedGet(BaseModel):
    action:str
    target:str
    post_id:int
    time:datetime.datetime
    user_id:int
    user:UserGet
    post:PostGet

    class Config():
        orm_mode = True