import psycopg2
import io
from .config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )

def fetch_master_data(conn):
    master_data = {}
    with conn.cursor() as cur:
        # Employees
        cur.execute("SELECT employee_id, office_id, hire_date, termination_date, employment_type FROM hr.employees")
        master_data['employees'] = [
            {
                'id': row[0], 'office_id': row[1], 'hire_date': row[2], 
                'termination_date': row[3], 'employment_type': row[4]
            } for row in cur.fetchall()
        ]
        
        # Offices
        cur.execute("SELECT office_id FROM office.offices")
        master_data['offices'] = [row[0] for row in cur.fetchall()]
        
        # Doors
        cur.execute("SELECT door_id, office_id, door_type FROM access.doors")
        master_data['doors'] = [
            {'id': row[0], 'office_id': row[1], 'type': row[2]} for row in cur.fetchall()
        ]
        
        # Rooms
        cur.execute("SELECT room_id, office_id, capacity FROM meeting.rooms")
        master_data['rooms'] = [
            {'id': row[0], 'office_id': row[1], 'capacity': row[2]} for row in cur.fetchall()
        ]
        
        # Devices
        cur.execute("SELECT device_id, device_type FROM iot.devices")
        master_data['devices'] = [
            {'id': row[0], 'type': row[1]} for row in cur.fetchall()
        ]
    return master_data

def bulk_insert(conn, table_name, columns, rows):
    """Efficiently bulk inserts rows using PostgreSQL COPY command."""
    if not rows:
        return
    csv_buffer = io.StringIO()
    for row in rows:
        formatted_row = []
        for col in row:
            if col is None:
                formatted_row.append(r'\N')
            else:
                # Basic string escaping for COPY
                val = str(col).replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                formatted_row.append(val)
        csv_buffer.write('\t'.join(formatted_row) + '\n')
    
    csv_buffer.seek(0)
    with conn.cursor() as cur:
        columns_str = ", ".join(columns)
        cur.copy_expert(f"COPY {table_name} ({columns_str}) FROM STDIN WITH NULL '\\N'", csv_buffer)
    conn.commit()
