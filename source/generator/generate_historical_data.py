import time
import os
import sys

# Ensure the root project dir is in sys.path if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from source.generator import config, db
from source.generator.historical import access_events, meeting_bookings, signing, device_events

def main():
    print(f"Starting Historical Data Generation (Scale: {config.DATA_SCALE})")
    print(f"Time Range: {config.HISTORY_START_DATE} to {config.HISTORY_END_DATE}")
    
    conn = db.get_connection()
    try:
        master_data = db.fetch_master_data(conn)
        
        # 1. Access Events
        events = access_events.generate_access_events(master_data, config)
        print(f"Bulk inserting {len(events)} access events...")
        start = time.time()
        db.bulk_insert(conn, 'access.access_events', 
            ['door_id', 'employee_id', 'event_time', 'access_type', 'status', 'created_at'], events)
        print(f"Inserted access events in {time.time() - start:.2f}s")
        del events
        
        # 2. Meeting Bookings
        bookings = meeting_bookings.generate_meeting_bookings(master_data, config)
        print(f"Bulk inserting {len(bookings)} bookings...")
        start = time.time()
        db.bulk_insert(conn, 'meeting.bookings',
            ['room_id', 'organizer_id', 'title', 'start_time', 'end_time', 'attendee_count', 'status', 'created_at', 'updated_at'], bookings)
        print(f"Inserted bookings in {time.time() - start:.2f}s")
        del bookings
        
        # 3. Signing Data
        docs, reqs = signing.generate_signing_data(master_data, config)
        print(f"Bulk inserting {len(docs)} documents and {len(reqs)} requests...")
        start = time.time()
        # Ensure document_id is specified since we mapped it manually for consistency
        db.bulk_insert(conn, 'signing.documents',
            ['document_id', 'document_code', 'title', 'document_type', 'creator_id', 'status', 'created_at', 'updated_at'], docs)
        
        db.bulk_insert(conn, 'signing.signing_requests',
            ['document_id', 'requester_id', 'signer_id', 'signing_order', 'status', 'requested_at', 'signed_at', 'rejected_at', 'created_at', 'updated_at'], reqs)
        print(f"Inserted signing data in {time.time() - start:.2f}s")
        del docs, reqs
        
        # 4. IoT Events
        iot_events = device_events.generate_device_events(master_data, config)
        print(f"Bulk inserting {len(iot_events)} IoT events...")
        start = time.time()
        db.bulk_insert(conn, 'iot.device_events',
            ['device_id', 'event_time', 'metric_type', 'metric_value', 'unit', 'created_at'], iot_events)
        print(f"Inserted IoT events in {time.time() - start:.2f}s")
        del iot_events
        
        print("Historical Data Generation Complete!")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
