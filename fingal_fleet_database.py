from sqlalchemy import create_engine, Column, String, JSON, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"
    id = Column(String, primary_key=True)
    config = Column(JSON, nullable=False)
    labels = Column(JSON, default=dict)
    last_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)
    current_soc = Column(Float)
    current_power_kw = Column(Float)

engine = create_engine(f"sqlite:///{os.path.abspath('data/fingal_fleet.db')}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)