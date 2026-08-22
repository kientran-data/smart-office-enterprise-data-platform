import random
import logging

logger = logging.getLogger(__name__)

DEVICE_METRICS = {
    "TEMPERATURE_SENSOR": ["TEMPERATURE"],
    "HUMIDITY_SENSOR": ["HUMIDITY"],
    "CO2_SENSOR": ["CO2"],
    "OCCUPANCY_SENSOR": ["OCCUPANCY"],
    "MULTI_SENSOR": ["TEMPERATURE", "HUMIDITY", "CO2", "OCCUPANCY"]
}

class IoTSimulator:
    def __init__(self, master_data):
        self.devices = master_data['devices']
        self.device_states = {}
        for d in self.devices:
            self.device_states[d['id']] = {
                'TEMPERATURE': random.uniform(22, 26),
                'HUMIDITY': random.uniform(40, 60),
                'CO2': random.uniform(400, 800),
                'OCCUPANCY': 0
            }
            
    def generate_event(self, conn, simulation_time):
        device = random.choice(self.devices)
        dev_id = device['id']
        dtype = device['type']
        
        metrics = DEVICE_METRICS.get(dtype, [])
        if not metrics:
            return
            
        if random.random() < 0.1:
            metric_type = 'HEARTBEAT'
            metric_value = 1.0
            unit = 'BOOL'
        else:
            metric_type = random.choice(metrics)
            is_day = 8 <= simulation_time.hour <= 18
            
            if metric_type == 'TEMPERATURE':
                change = random.uniform(-0.3, 0.3)
                unit = 'C'
            elif metric_type == 'HUMIDITY':
                change = random.uniform(-1.0, 1.0)
                unit = '%'
            elif metric_type == 'CO2':
                change = random.uniform(-10.0, 10.0)
                unit = 'ppm'
            elif metric_type == 'OCCUPANCY':
                target = random.randint(0, 20) if is_day else 0
                change = (target - self.device_states[dev_id]['OCCUPANCY']) * random.uniform(0.1, 0.5)
                unit = 'COUNT'
                
            new_val = self.device_states[dev_id][metric_type] + change
            
            if metric_type == 'TEMPERATURE': new_val = max(18, min(32, new_val))
            elif metric_type == 'HUMIDITY': new_val = max(35, min(85, new_val))
            elif metric_type == 'CO2': new_val = max(350, min(1800, new_val))
            elif metric_type == 'OCCUPANCY': new_val = max(0, min(100, new_val))
                
            self.device_states[dev_id][metric_type] = new_val
            metric_value = round(new_val, 2)
            
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO iot.device_events (device_id, event_time, metric_type, metric_value, unit, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (dev_id, simulation_time, metric_type, metric_value, unit, simulation_time)
            )
        conn.commit()
        logger.info("IOT device=%s metric=%s value=%s", dev_id, metric_type, metric_value)
