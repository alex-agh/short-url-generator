from pydantic import BaseModel
from pydantic import validator

from .config import BASE_URL, PATH_LENGTH

class URL(BaseModel):
    long_url: str

class ShortURL(BaseModel):
    short_url: str

    @validator("short_url")
    def validate_custom_url_format(cls, value):
        if not value.startswith(BASE_URL):
            raise ValueError(f"URL should start with {BASE_URL}.")

        path = value[len(BASE_URL):]

        if len(path) != PATH_LENGTH:
            raise ValueError("Provided path is incorrect.")

        return value
