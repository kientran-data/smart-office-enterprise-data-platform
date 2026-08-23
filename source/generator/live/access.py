import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AccessSimulator:
    def __init__(self, master_data):
        self.employees = master_data['employees']
        self.doors = master_data['doors']
        self.employee_presence = {emp['id']: False for emp in self.employees}
        
    def get_probability_by_hour(self, hour):
        if 7 <= hour < 10:
            return {'IN': 0.8, 'OUT': 0.1}
        elif 11 <= hour < 14:
            return {'IN': 0.4, 'OUT': 0.4}
        elif 16 <= hour < 19:
            return {'IN': 0.1, 'OUT': 0.8}
        elif 22 <= hour or hour < 6:
            return {'IN': 0.01, 'OUT': 0.05}
        else:
            return {'IN': 0.2, 'OUT': 0.2}

    def generate_event(self, conn, simulation_time):
        hour = simulation_time.hour
        probs = self.get_probability_by_hour(hour)
        
        emp = random.choice(self.employees)
        emp_id = emp['id']
        is_in = self.employee_presence[emp_id]
        
        if is_in:
            action = 'OUT'
            prob = probs['OUT']
        else:
            action = 'IN'
            prob = probs['IN']
            
        if random.random() > prob:
            return
            
        office_id = emp['office_id']
        if random.random() < 0.05:
            office_id = random.choice([d['office_id'] for d in self.doors])
            
        valid_doors = [d for d in self.doors if d['office_id'] == office_id]
        if not valid_doors:
            return
            
        door = random.choice(valid_doors)
        status = 'SUCCESS'
        
        if random.random() < 0.01:
            status = 'DENIED'
            door = random.choice([d for d in valid_doors if d['type'] == 'RESTRICTED'] or valid_doors)
            
        if status == 'SUCCESS':
            self.employee_presence[emp_id] = (action == 'IN')
            
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO access.access_events (employee_id, door_id, event_time, access_type, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (emp_id, door['id'], simulation_time, action, status, datetime.now())
            )
        conn.commit()
        logger.info("ACCESS employee=%s type=%s status=%s door=%s", emp_id, action, status, door['id'])
