from datetime import datetime, timedelta, time
import pytz

def convert_utc_to_local(utc_dt, timezone_str):
    """
    Converts a UTC datetime object to the target local timezone.
    """
    local_tz = pytz.timezone(timezone_str)
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

def convert_local_to_utc(local_dt, timezone_str):
    """
    Converts a local datetime object to UTC.
    """
    local_tz = pytz.timezone(timezone_str)
    return local_tz.localize(local_dt).astimezone(pytz.utc)

def get_overlap(start1, end1, start2, end2):
    """
    Calculate the overlap between two time intervals.
    Returns timedelta.
    """
    latest_start = max(start1, start2)
    earliest_end = min(end1, end2)
    delta = (earliest_end - latest_start).total_seconds()
    return max(0, delta)

def interpolate_uptime_downtime(observations, business_start, business_end):
    """
    Interpolates uptime and downtime for a store within a business interval based on observations.
    Returns: uptime_seconds, downtime_seconds
    """
    if not observations:
        return 0, (business_end - business_start).total_seconds()

    observations.sort(key=lambda x: x['timestamp'])
    total_uptime = 0
    total_downtime = 0

    periods = []

    for i in range(len(observations) - 1):
        start = observations[i]['timestamp']
        end = observations[i + 1]['timestamp']
        status = observations[i]['status']

        # clip to business hours
        clip_start = max(start, business_start)
        clip_end = min(end, business_end)

        if clip_start >= clip_end:
            continue

        duration = (clip_end - clip_start).total_seconds()

        if status == 'active':
            total_uptime += duration
        else:
            total_downtime += duration

    first = observations[0] # handle before first observation
    if first['timestamp'] > business_start:
        assumed_duration = (first['timestamp'] - business_start).total_seconds()
        if first['status'] == 'active':
            total_uptime += assumed_duration
        else:
            total_downtime += assumed_duration

    last = observations[-1] # handle after last observation
    if last['timestamp'] < business_end:
        assumed_duration = (business_end - last['timestamp']).total_seconds()
        if last['status'] == 'active':
            total_uptime += assumed_duration
        else:
            total_downtime += assumed_duration

    return total_uptime, total_downtime
