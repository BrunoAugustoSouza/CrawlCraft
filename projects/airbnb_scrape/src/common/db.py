# Database imports
from sqlalchemy import create_engine, Column, \
    String, Text, Integer, Boolean, Date, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import uuid

# --- Database Setup ---
# Use an in-memory SQLite database for simplicity.
# For a production application, you'd use a file-based SQLite, PostgreSQL, MySQL, etc.
DATABASE_URL = "sqlite:///data/sql/scraped_data.db" # This will create a file named scraped_data.db


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define your database model
class HomesUrl(Base):
    __tablename__ = 'first_page_info'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # nova PK
    scrape_job_id = Column(String, nullable=False)  # pode ter duplicatas
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)

# Define your database model
class Price(Base):
    __tablename__ = 'price'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # nova PK
    scrapeJobId = Column(String, nullable=False)  # pode ter duplicatas
    isPropertyAvailable = Column(Boolean, nullable=False)
    url = Column(Text, nullable=True)
    roomId = Column(String, nullable=True)
    checkIn = Column(Date, nullable=True)
    checkOut = Column(Date, nullable=True)
    productId = Column(String, nullable=True)
    adults = Column(Integer, nullable=True)
    currency = Column(String, nullable=True)
    priceTotal = Column(Float, nullable=True)
    discountedPrice = Column(Float, nullable=True)
    originalPrice = Column(Float, nullable=True)
    priceNightTotal = Column(Float, nullable=True)
    longStayDiscount = Column(Float, nullable=True)
    resortFee = Column(Float, nullable=True)
    taxesAndFees = Column(Float, nullable=True)
    priceAfterDiscount = Column(Float, nullable=True)
    numberOfNights = Column(Integer, nullable=True)
    
# Create tables if they don't exist
Base.metadata.create_all(engine)