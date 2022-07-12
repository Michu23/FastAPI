from turtle import title
from fastapi import FastAPI,Depends,status,Response,HTTPException

from blog.schemas import Blog
from . import models, schemas

from sqlalchemy.orm import Session

from .database import engine,SessionLocal
import blog

from typing import List

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/blog',status_code=status.HTTP_201_CREATED)
def create_blog(request: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get('/allblogs',response_model=List[schemas.ShowBlog])
def get_blogs(db: Session = Depends(get_db)):
    return db.query(models.Blog).all()


@app.get('/blog/{id}',status_code=200,response_model=schemas.ShowBlog)
def get_blog(id: int,response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {"detail": f"Blog with id {id} not found"}
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    else:
        return blog


@app.delete('/blog/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    else:
        db.delete(blog)
        db.commit()
        return {"detail": f"Blog with id {id} deleted"}

@app.put('/blog/{id}',status_code=status.HTTP_200_OK)
def update_blog(id: int, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    else:
        blog.title = request.title
        blog.body = request.body
        db.commit()
        return blog

@app.patch('/blog/{id}',status_code=status.HTTP_200_OK)
def patch_blog(id: int, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    else:
        if request.title:
            blog.title = request.title
        if request.body:
            blog.body = request.body
        db.commit()
        return blog