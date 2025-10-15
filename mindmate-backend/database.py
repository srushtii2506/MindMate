from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database URL
DATABASE_URL = "sqlite:///./mindmate.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# User table model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Feedback table model
class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    country = Column(String)
    message = Column(Text)
    rating = Column(Integer)

# Exercise table model
class Exercise(Base):
    __tablename__ = "exercise"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)

# Diet table model
class Diet(Base):
    __tablename__ = "diet"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)

# Video table model
class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String)

# StressResult table model
class StressResult(Base):
    __tablename__ = "stress_results"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    sleep = Column(Float)
    bp = Column(String)  # Changed from Float to String to store "120/80" format
    resp = Column(Float)
    heart = Column(Float)
    stress_level = Column(String)
    advice = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Admin table model
class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
