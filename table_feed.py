from database import Base, engine, SessionLocal
from sqlalchemy import Column, String, Integer, func, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from table_post import Post
from table_user import User


class Feed (Base):
    __tablename__ = "feed_data"
    __table_args__ = {"schema": "public"}
    action = Column (String)
    target = Column (Integer)
    post_id = Column (Integer, ForeignKey(Post.post_id), primary_key=True)
    post = relationship("Post")
    timestamp = Column (TIMESTAMP)
    user_id = Column (Integer, ForeignKey(User.user_id), primary_key=True)
    user = relationship("User")

"""
if __name__ == "__main__":
    session = SessionLocal()

    result = session.query(Post).filter(Post.topic == 'business')\
                    .order_by(Post.id.desc()).limit(10).all()

    result_list = []
    for x in result:
        result_list.append(
            x.id
        )

    print(result_list)
    
    result = session.query(User.country, User.os, func.count().label('count'))\
                    .filter(User.exp_group == 3)\
                    .group_by (User.country, User.os)\
                    .having (func.count()>100)\
                    .order_by(func.count().desc()).all()

    result_list = []
    for x in result:
        result_list.append(
            (x.country, x.os, x.count)
        )

    print (result_list)
    """