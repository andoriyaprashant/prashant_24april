from sqlalchemy import Column, Integer, String, DateTime, Time
from app.database import Base
import pytz
from datetime import datetime

class StoreStatus(Base):
    __tablename__ = "store_status"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    timestamp_utc = Column(DateTime)
    status = Column(String)  # 'active' or 'inactive'

class StoreBusinessHours(Base):
    __tablename__ = "store_business_hours"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    day_of_week = Column(Integer)  # 0 = Monday
    start_time_local = Column(Time)
    end_time_local = Column(Time)

class StoreTimezone(Base):
    __tablename__ = "store_timezones"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    timezone_str = Column(String) 
