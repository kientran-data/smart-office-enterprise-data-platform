import random
from datetime import timedelta, datetime
from tqdm import tqdm
from ..utils import date_range

def generate_meeting_bookings(master_data, config):
    print("Generating Meeting Bookings...")
    employees = master_data['employees']
    rooms = master_data['rooms']
    
    start_date = config.HISTORY_START_DATE
    end_date = config.HISTORY_END_DATE
    
    bookings_to_insert = []
    
    durations = [30, 60, 90, 120]
    duration_weights = [0.25, 0.50, 0.15, 0.10]
    
    for current_date in tqdm(list(date_range(start_date, end_date)), desc="Meeting Bookings"):
        is_weekend = current_date.weekday() >= 5
        
        schedule_tracker = {r['id']: [] for r in rooms}
        
        for room in rooms:
            num_bookings = random.randint(0, 1) if is_weekend else random.randint(1, 4)
                
            for _ in range(num_bookings):
                duration_mins = random.choices(durations, weights=duration_weights, k=1)[0]
                
                for _retry in range(5):
                    start_hour = random.uniform(8.0, 17.0)
                    start_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=start_hour)
                    end_time = start_time + timedelta(minutes=duration_mins)
                    
                    overlap = False
                    for existing_start, existing_end in schedule_tracker[room['id']]:
                        if start_time < existing_end and end_time > existing_start:
                            overlap = True
                            break
                            
                    if not overlap:
                        schedule_tracker[room['id']].append((start_time, end_time))
                        valid_emps = [e for e in employees if e['hire_date'] <= current_date and (not e['termination_date'] or e['termination_date'] >= current_date)]
                        if not valid_emps:
                            break
                            
                        organizer = random.choice(valid_emps)
                        attendee_count = random.randint(2, room['capacity'])
                        
                        status = random.choices(
                            ['COMPLETED', 'CANCELLED', 'NO_SHOW'],
                            weights=[0.75, 0.15, 0.10], k=1
                        )[0]
                        
                        title = f"Meeting - {room['id']} - {start_time.strftime('%H:%M')}"
                        
                        # created_at and updated_at set prior to start_time
                        bookings_to_insert.append((
                            room['id'], organizer['id'], title, start_time, end_time, attendee_count, status, start_time - timedelta(days=1), start_time - timedelta(days=1)
                        ))
                        break
                        
    return bookings_to_insert
