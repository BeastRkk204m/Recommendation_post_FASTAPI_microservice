import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from typing import List
from catboost import CatBoostClassifier
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, func
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PostGet(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        orm_mode = True


def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  
        MODEL_PATH = '/workdir/user_input/model.cbm'
    else:
        MODEL_PATH = path
    return MODEL_PATH


def load_models():
    model_path = get_model_path("model.cbm")
    
    from_file = CatBoostClassifier()
    model = from_file.load_model(model_path, format='cbm')
    return model


def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 200000
    engine = create_engine(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@postgres.lab.karpov.courses:6432/startml"
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)

model = load_models()
df_users = batch_load_sql('SELECT * FROM user_features_encoded_22')
df_posts = batch_load_sql('SELECT * FROM public.post_text_df')
df_posts_mod = batch_load_sql('SELECT * FROM post_features_encoded_22')

def compose_user_posts(user_id, timestamp):
    # Формирует таблицу из данных одного юзера и всех постов
    
    df_table = pd.concat([(df_users[df_users['user_id'] == user_id].reset_index(drop=True)), df_posts_mod], axis=1).reset_index(drop=True).drop('index', axis=1)
   
    for column in df_users.drop('index', axis=1).columns:
            df_table.loc[df_table[column].isna(), column] = df_table.loc[0, column]

    df_table = df_table.drop( 'user_id', axis=1)

    df_table['timestamp'] = pd.Timestamp(timestamp)
    df_table['timestamp'] = df_table['timestamp'].astype('int64')

    return df_table



app = FastAPI()

def get_db():
    with SessionLocal() as db:
        return db

@app.get("/post/recommendations/", response_model=List[PostGet])
def get_post(id: int, time: datetime, limit: int = 5, db: Session = Depends(get_db)) -> List[PostGet]:

    df_table = compose_user_posts(id, time)

    # Получает массив из 5 id постов
    post_id = pd.concat([df_table['post_id'], pd.DataFrame(model.predict_proba(df_table).T[1], columns=['prediction'])], axis=1).sort_values(by=['prediction'], ascending=False).head(5)['post_id'].values

    # Поучает нужные посты из таблицы постов
    dfs_to_concat = []

    for i in post_id:
        filtered_df = df_posts[df_posts['post_id'] == i]
        dfs_to_concat.append(filtered_df)
    
    result_table = pd.concat(dfs_to_concat)
    result = []
    for i in range(5):
        result.append(PostGet(id=result_table['post_id'].iloc[i], text=result_table['text'].iloc[i], topic=result_table['topic'].iloc[i]))

    if result == []:
        raise HTTPException(404)
    else:
        return result

