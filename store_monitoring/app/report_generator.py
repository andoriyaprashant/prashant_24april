from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
from app import models, utils
from app.database import SessionLocal
import pytz
import os
import uuid
import threading

report_status = {}

def start_report_generation():
    report_id = str(uuid.uuid4())
    report_status[report_id] = "Running"

    def background_task():
        try:
            generate_report(report_id)
            report_status[report_id] = "Complete"
            print(f"Report {report_id} marked as Complete")
        except Exception as e:
            print(f"Report generation failed for {report_id}: {e}")
            report_status[report_id] = "Failed"


    thread = threading.Thread(target=background_task)
    thread.start()

    return report_id

def get_report_status(report_id):
    return report_status.get(report_id, "Invalid Report ID")

def make_timezone_aware(dt, tz_str="UTC"):
    if dt.tzinfo is None: 
        return pytz.timezone(tz_str).localize(dt) 
    return dt 


def generate_report(report_id):
    db = SessionLocal()

    stores = db.query(models.StoreStatus.store_id).distinct().all()
    stores = [s[0] for s in stores]

    report_data = []

    max_timestamp = db.query(func.max(models.StoreStatus.timestamp_utc)).scalar()

    if max_timestamp is not None:
        max_timestamp = make_timezone_aware(max_timestamp, "UTC")
    else:
        print("No max timestamp found!")
        return 

    for store_id in stores:
        timezone_entry = db.query(models.StoreTimezone).filter_by(store_id=store_id).first()
        timezone_str = timezone_entry.timezone_str if timezone_entry else "America/Chicago"

        # Period windows (utc)
        periods = {
            "last_hour": (max_timestamp - timedelta(hours=1), max_timestamp),
            "last_day": (max_timestamp - timedelta(days=1), max_timestamp),
            "last_week": (max_timestamp - timedelta(weeks=1), max_timestamp),
        }

        store_row = {"store_id": store_id}

        for period_name, (start_time, end_time) in periods.items():
            uptime_seconds = 0
            downtime_seconds = 0

            start_time = make_timezone_aware(start_time, "UTC")
            end_time = make_timezone_aware(end_time, "UTC")
            # Loop through each day in this window
            day_cursor = start_time.date()
            while day_cursor <= end_time.date():
                business_hours = db.query(models.StoreBusinessHours).filter_by(
                    store_id=store_id,
                    day_of_week=day_cursor.weekday()
                ).all()

                if not business_hours:
                    bh_start_local = datetime.combine(day_cursor, datetime.min.time())
                    bh_end_local = datetime.combine(day_cursor, datetime.max.time().replace(microsecond=0))
                    business_hours = [(bh_start_local.time(), bh_end_local.time())]
                else:
                    business_hours = [(b.start_time_local, b.end_time_local) for b in business_hours]

                for bh_start_time, bh_end_time in business_hours:
                    local_tz = pytz.timezone(timezone_str)

                    bh_start_local_dt = datetime.combine(day_cursor, bh_start_time)
                    bh_end_local_dt = datetime.combine(day_cursor, bh_end_time)

                    # Convert local times to UTC
                    bh_start_utc = utils.convert_local_to_utc(bh_start_local_dt, timezone_str)
                    bh_end_utc = utils.convert_local_to_utc(bh_end_local_dt, timezone_str)

                    # Ensure bh_start_utc and bh_end_utc are timezone-aware (UTC)
                    bh_start_utc = make_timezone_aware(bh_start_utc, "UTC")
                    bh_end_utc = make_timezone_aware(bh_end_utc, "UTC")

                    effective_start = max(bh_start_utc, start_time)
                    effective_end = min(bh_end_utc, end_time)

                    if effective_start >= effective_end:
                        continue

                    observations = db.query(models.StoreStatus).filter(
                        models.StoreStatus.store_id == store_id,
                        models.StoreStatus.timestamp_utc >= effective_start,
                        models.StoreStatus.timestamp_utc <= effective_end
                    ).order_by(models.StoreStatus.timestamp_utc).all()

                    observation_list = [
                        {"timestamp": make_timezone_aware(obs.timestamp_utc, "UTC"), "status": obs.status}
                        for obs in observations
                    ]


                    up, down = utils.interpolate_uptime_downtime(
                        observation_list,
                        effective_start,
                        effective_end
                    )

                    uptime_seconds += up
                    downtime_seconds += down

                day_cursor += timedelta(days=1)

            # Storing results in minutes or hours based on the period
            if "hour" in period_name:
                store_row[f"uptime_{period_name}"] = round(uptime_seconds / 60, 2) 
                store_row[f"downtime_{period_name}"] = round(downtime_seconds / 60, 2) 
            else:
                store_row[f"uptime_{period_name}"] = round(uptime_seconds / 3600, 2) 
                store_row[f"downtime_{period_name}"] = round(downtime_seconds / 3600, 2)

        report_data.append(store_row)

    db.close()

    output_folder = os.path.join(os.getcwd(), "reports")
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"report_{report_id}.csv")

    print(f"Saving report to: {output_file}")

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = [
            "store_id",
            "uptime_last_hour", "uptime_last_day", "uptime_last_week",
            "downtime_last_hour", "downtime_last_day", "downtime_last_week"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in report_data:
            writer.writerow({
                "store_id": row["store_id"],
                "uptime_last_hour": row["uptime_last_hour"],
                "uptime_last_day": row["uptime_last_day"],
                "uptime_last_week": row["uptime_last_week"],
                "downtime_last_hour": row["downtime_last_hour"],
                "downtime_last_day": row["downtime_last_day"],
                "downtime_last_week": row["downtime_last_week"],
            })
