import random
from datetime import timedelta
from tqdm import tqdm
from ..utils import date_range, get_gaussian_time

def generate_access_events(master_data, config):
    print("Generating Access Events...")
    employees = master_data['employees']
    doors_by_office = {}
    for d in master_data['doors']:
        doors_by_office.setdefault(d['office_id'], []).append(d)
        
    start_date = config.HISTORY_START_DATE
    end_date = config.HISTORY_END_DATE
    
    events_to_insert = []
    
    for current_date in tqdm(list(date_range(start_date, end_date)), desc="Access Events"):
        is_weekend = current_date.weekday() >= 5
        
        for emp in employees:
            if current_date < emp['hire_date']:
                continue
            if emp['termination_date'] and current_date > emp['termination_date']:
                continue
                
            prob = 0.03 if is_weekend else {
                'FULL_TIME': 0.70,
                'PART_TIME': 0.45,
                'CONTRACT': 0.50,
                'INTERN': 0.75
            }.get(emp['employment_type'], 0.70)
            
            if random.random() > prob:
                continue
                
            visited_office = emp['office_id']
            if random.random() < 0.05:
                other_offices = [o for o in master_data['offices'] if o != emp['office_id']]
                if other_offices:
                    visited_office = random.choice(other_offices)
                    
            office_doors = doors_by_office.get(visited_office, [])
            entry_doors = [d for d in office_doors if d['type'] == 'ENTRY']
            exit_doors = [d for d in office_doors if d['type'] == 'EXIT']
            restricted_doors = [d for d in office_doors if d['type'] == 'RESTRICTED']
            
            if not entry_doors or not exit_doors:
                continue
                
            in_time = get_gaussian_time(current_date, mu_hour=8.5, sigma_hour=0.65)
            
            if random.random() < 0.01 and restricted_doors:
                denied_door = random.choice(restricted_doors)
                denied_time = in_time - timedelta(minutes=random.randint(1, 15))
                events_to_insert.append((
                    denied_door['id'], emp['id'], denied_time, 'IN', 'DENIED', denied_time + timedelta(seconds=2)
                ))
            
            in_door = random.choice(entry_doors)
            events_to_insert.append((
                in_door['id'], emp['id'], in_time, 'IN', 'SUCCESS', in_time + timedelta(seconds=2)
            ))
            
            work_duration = timedelta(hours=random.uniform(8, 10))
            out_time = in_time + work_duration
            out_door = random.choice(exit_doors)
            
            events_to_insert.append((
                out_door['id'], emp['id'], out_time, 'OUT', 'SUCCESS', out_time + timedelta(seconds=2)
            ))
            
    return events_to_insert
