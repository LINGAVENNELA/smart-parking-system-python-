import time

def parked_duration(entry_time):
    elapsed = time.time() - entry_time
    minutes = int(elapsed // 60)
    return f"{minutes} mins"
