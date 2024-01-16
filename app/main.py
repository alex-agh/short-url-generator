from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import RedirectResponse

from .config import BASE_URL, PATH_LENGTH

from . import schemas

import random, string
import validators

from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "URL Shortener API",
    version = "0.0.1",
)

def generate_url_path(path_length):
    """
    Generate a random url path.
    """
    
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(path_length))

    return random_string

@app.post("/shorten-url", status_code=status.HTTP_201_CREATED, description="Generate short URL.")
def shorten_url(url: schemas.URL, db: Session = Depends(get_db)):
    if not validators.url(url.long_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid URL input.')

    existing_url = (
        db.query(models.URLModel)
        .filter(models.URLModel.long_url == url.long_url)
        .first()
    )

    if existing_url:
        path = existing_url.short_url_path
    else:
        while True:
            path = generate_url_path(PATH_LENGTH)
            existing_path = db.query(models.URLModel).filter(models.URLModel.short_url_path == path).first()
            
            if not existing_path:
                break
        
        new_url = models.URLModel(long_url=url.long_url, short_url_path=path)
        
        db.add(new_url)
        db.commit()
        db.refresh(new_url)
    
    short_url = ''.join([BASE_URL, path])
    return {"short_url": short_url}

@app.get("/{url_path}")
def redirect_to(url_path: str, db: Session = Depends(get_db)):
    """
    Redirect to the full url.

    Please use the browser address bar to test this endpoint!
    """
    
    if len(url_path) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid URL path.')
    
    full_url = (
        db.query(models.URLModel)
        .filter(models.URLModel.short_url_path == url_path)
        .first()
    )

    if not full_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not matches found for the given URL.')
    return RedirectResponse(full_url.long_url)

@app.delete("/remove", status_code=status.HTTP_204_NO_CONTENT, description="Delete given URL by providing short URL.")
def delete_url(short_url: schemas.ShortURL, db: Session = Depends(get_db)):
    path = short_url.short_url[-PATH_LENGTH:]

    db_url = db.query(models.URLModel).filter(models.URLModel.short_url_path == path).first()
    
    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")

    db.delete(db_url)
    db.commit()
    
    return None
