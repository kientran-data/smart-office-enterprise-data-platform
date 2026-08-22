import random
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class MeetingSimulator:
    def __init__(self, master_data):
        self.rooms = master_data['rooms']
        self.employees = master_data['employees']
        
    def create_booking(self, conn, simulation_time):
        room = random.choice(self.rooms)
        organizer = random.choice(self.employees)
        
        start_time = simulation_time + timedelta(minutes=random.randint(60, 4320))
        start_time = start_time.replace(minute=(start_time.minute // 30) * 30, second=0, microsecond=0)
        
        duration = random.choice([30, 60, 90, 120])
        end_time = start_time + timedelta(minutes=duration)
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM meeting.bookings 
                WHERE room_id = %s AND status NOT IN ('CANCELLED') 
                AND start_time < %s AND end_time > %s LIMIT 1
            """, (room['id'], end_time, start_time))
            
            if cur.fetchone():
                return # Overlap
                
            attendees = random.randint(2, max(2, room['capacity']))
            title = f"Live Sync - {room['id']}"
            
            cur.execute("""
                INSERT INTO meeting.bookings (room_id, organizer_id, title, start_time, end_time, attendee_count, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', %s, %s) RETURNING booking_id
            """, (room['id'], organizer['id'], title, start_time, end_time, attendees, simulation_time, simulation_time))
            
            bk_id = cur.fetchone()[0]
        conn.commit()
        logger.info("BOOKING CREATE booking=%s room=%s start=%s", bk_id, room['id'], start_time)
        
    def update_booking(self, conn, simulation_time):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT booking_id, start_time, end_time, status 
                FROM meeting.bookings 
                WHERE status IN ('PENDING', 'CONFIRMED') 
                ORDER BY RANDOM() LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                return
                
            bk_id, start_time, end_time, status = row
            
            new_status = None
            if status == 'PENDING' and simulation_time >= start_time - timedelta(minutes=30):
                new_status = random.choices(['CONFIRMED', 'CANCELLED'], weights=[0.9, 0.1])[0]
            elif status == 'CONFIRMED' and simulation_time > end_time:
                new_status = random.choices(['COMPLETED', 'NO_SHOW'], weights=[0.9, 0.1])[0]
                
            if new_status:
                cur.execute("UPDATE meeting.bookings SET status = %s, updated_at = %s WHERE booking_id = %s", (new_status, simulation_time, bk_id))
                conn.commit()
                logger.info("BOOKING UPDATE booking=%s %s -> %s", bk_id, status, new_status)
