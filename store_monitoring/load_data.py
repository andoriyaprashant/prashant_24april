import pandas as pd
from app.database import SessionLocal, engine
from app import models
from datetime import datetime

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def load_store_status():
    print("Loading store_status.csv...")
    df = pd.read_csv("data/store_status.csv")
    for _, row in df.iterrows():
        timestamp = row['timestamp_utc'].replace(" UTC", "")
        db.add(models.StoreStatus(
            store_id=row['store_id'],
            timestamp_utc=datetime.fromisoformat(timestamp),
            status=row['status']
        ))

def load_store_business_hours():
    print("Loading menu_hours.csv...")
    df = pd.read_csv("data/menu_hours.csv")
    for _, row in df.iterrows():
        db.add(models.StoreBusinessHours(
            store_id=row['store_id'],
            day_of_week=row['dayOfWeek'],
            start_time_local=datetime.strptime(row['start_time_local'], "%H:%M:%S").time(),
            end_time_local=datetime.strptime(row['end_time_local'], "%H:%M:%S").time()
        ))


def load_store_timezones():
    print("Loading timezones.csv...")
    df = pd.read_csv("data/timezones.csv")
    for _, row in df.iterrows():
        db.add(models.StoreTimezone(
            store_id=row['store_id'],
            timezone_str=row['timezone_str']
        ))
load_store_status()
load_store_business_hours()
load_store_timezones()

db.commit()
db.close()
print("All data loaded into the database.")
