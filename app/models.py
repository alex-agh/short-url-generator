from .database import Base

from sqlalchemy import Column, String

class URLModel(Base):
    __tablename__ = 'urls'

    long_url = Column(String, nullable=False)
    short_url_path = Column(String, nullable=False, primary_key=True)