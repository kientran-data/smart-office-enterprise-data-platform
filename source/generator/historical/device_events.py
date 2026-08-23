import random
from datetime import timedelta, datetime
from tqdm import tqdm
from ..utils import date_range

def generate_device_events(master_data, config):
    print("Generating IoT Device Events...")
    devices = master_data['devices']
    
    start_date = config.HISTORY_START_DATE
    end_date = config.HISTORY_END_DATE
    
    events_to_insert = []
    events_per_day = 8
    
    for current_date in tqdm(list(date_range(start_date, end_date)), desc="IoT Events"):
        for device in devices:
            dtype = device['type']
            
            for _ in range(events_per_day):
                hour = random.uniform(0, 24)
                event_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour)
                created_at = event_time + timedelta(seconds=random.randint(1, 5))
                
                is_day = 8 <= hour <= 18
                
                if dtype == 'TEMPERATURE_SENSOR':
                    metric_type = 'TEMPERATURE'
                    unit = 'C'
                    val = random.uniform(23, 27) if is_day else random.uniform(19, 23)
                elif dtype == 'HUMIDITY_SENSOR':
                    metric_type = 'HUMIDITY'
                    unit = '%'
                    val = random.uniform(40, 60)
                elif dtype == 'CO2_SENSOR':
                    metric_type = 'CO2'
                    unit = 'ppm'
                    val = random.uniform(600, 1200) if is_day else random.uniform(350, 500)
                elif dtype == 'OCCUPANCY_SENSOR':
                    metric_type = 'OCCUPANCY'
                    unit = 'COUNT'
                    val = random.randint(1, 20) if is_day else 0
                elif dtype == 'MULTI_SENSOR':
                    metric_type = random.choice(['TEMPERATURE', 'HUMIDITY', 'CO2'])
                    if metric_type == 'TEMPERATURE':
                        unit = 'C'
                        val = random.uniform(23, 27) if is_day else random.uniform(19, 23)
                    elif metric_type == 'HUMIDITY':
                        unit = '%'
                        val = random.uniform(40, 60)
                    else:
                        unit = 'ppm'
                        val = random.uniform(600, 1200) if is_day else random.uniform(350, 500)
                else:
                    continue
                    
                events_to_insert.append((
                    device['id'], event_time, metric_type, round(val, 2), unit, created_at
                ))
                
            # 1 Heartbeat per day
            hb_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.uniform(0, 24))
            events_to_insert.append((
                device['id'], hb_time, 'HEARTBEAT', 1.00, 'BOOL', hb_time + timedelta(seconds=2)
            ))
            
    return events_to_insert
