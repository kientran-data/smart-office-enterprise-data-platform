import os
import random
from datetime import date, timedelta
from faker import Faker
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# 1. Deterministic configuration
fake = Faker()
Faker.seed(42)
random.seed(42)

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("SOURCE_POSTGRES_DB", "smart_office")
DB_USER = os.getenv("SOURCE_POSTGRES_USER", "smartoffice_admin")
DB_PASS = os.getenv("SOURCE_POSTGRES_PASSWORD", "smartoffice_password")
DB_HOST = os.getenv("SOURCE_POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("SOURCE_POSTGRES_PORT", "5434")

# Distribution definitions
DEPARTMENT_COUNTS = {
    'EXEC': 3,
    'HR': 25,
    'FIN': 40,
    'DATA': 45,
    'ENG': 140,
    'PRODUCT': 60,
    'MKT': 70,
    'OPS': 55,
    'LEGAL': 20,
    'IT': 42
}

OFFICE_WEIGHTS = {
    'HN01': 0.60,
    'HCM01': 0.25,
    'DN01': 0.15
}

DEPARTMENT_POSITIONS = {
    "EXEC": ["CEO", "CFO", "CTO"],
    "HR": ["HR_MANAGER", "HR_SPECIALIST"],
    "FIN": ["FIN_MANAGER", "ACCOUNTANT", "FIN_ANALYST"],
    "DATA": ["DATA_MANAGER", "DATA_ENGINEER", "DATA_ANALYST", "DATA_SCIENTIST"],
    "ENG": ["ENG_MANAGER", "BACKEND_ENGINEER", "FRONTEND_ENGINEER", "MOBILE_ENGINEER", "QA_ENGINEER"],
    "PRODUCT": ["PRODUCT_MANAGER", "BUSINESS_ANALYST", "PRODUCT_OWNER"],
    "MKT": ["MKT_MANAGER", "PERFORMANCE_MARKETER", "CONTENT_SPECIALIST"],
    "OPS": ["OPS_MANAGER", "OPS_SPECIALIST"],
    "LEGAL": ["LEGAL_MANAGER", "LEGAL_SPECIALIST"],
    "IT": ["IT_MANAGER", "SYSTEM_ADMIN", "IT_SUPPORT"]
}

ROOM_COUNTS = {
    'HN01': 16,
    'HCM01': 8,
    'DN01': 6
}
ROOM_CAPACITIES = [4, 6, 8, 10, 12, 20]
ROOM_CAPACITY_WEIGHTS = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

def fetch_reference_data(cur):
    cur.execute("SELECT department_id, department_code FROM hr.departments WHERE status = 'ACTIVE'")
    departments = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT position_id, position_code, level FROM hr.positions WHERE status = 'ACTIVE'")
    positions = {row[1]: {'id': row[0], 'level': row[2]} for row in cur.fetchall()}

    cur.execute("SELECT office_id, office_code FROM office.offices WHERE status = 'ACTIVE'")
    offices = {row[1]: row[0] for row in cur.fetchall()}

    return departments, positions, offices

def generate_employees(cur, departments, positions, offices):
    print("Generating 500 Employees...")
    employees_to_insert = []
    
    office_codes = list(OFFICE_WEIGHTS.keys())
    office_probs = list(OFFICE_WEIGHTS.values())
    
    emp_counter = 1
    
    # Generate EXECs first
    exec_dept_id = departments['EXEC']
    for pos_code in DEPARTMENT_POSITIONS['EXEC']:
        emp_code = f"EMP{emp_counter:06d}"
        pos_id = positions[pos_code]['id']
        office_code = 'HN01' # Execs in HQ
        office_id = offices[office_code]
        
        full_name = fake.name()
        email = f"{emp_code.lower()}@smartoffice.local"
        phone = fake.phone_number()[:50]
        hire_date = fake.date_between(start_date='-5y', end_date='-1y')
        
        employees_to_insert.append((
            emp_code, full_name, email, phone, exec_dept_id, pos_id, office_id, hire_date
        ))
        emp_counter += 1

    # Generate the rest
    for dept_code, count in DEPARTMENT_COUNTS.items():
        if dept_code == 'EXEC':
            continue
            
        dept_id = departments[dept_code]
        dept_pos_codes = DEPARTMENT_POSITIONS[dept_code]
        
        # Determine manager position
        manager_pos = next((p for p in dept_pos_codes if positions[p]['level'] == 'MANAGER'), None)
        staff_positions = [p for p in dept_pos_codes if p != manager_pos]
        
        for i in range(count):
            emp_code = f"EMP{emp_counter:06d}"
            office_code = random.choices(office_codes, weights=office_probs, k=1)[0]
            office_id = offices[office_code]
            
            # Ensure at least 1 manager per department (assign manager to the first employee generated)
            if i == 0 and manager_pos:
                pos_code = manager_pos
            else:
                pos_code = random.choice(staff_positions)
                
            pos_id = positions[pos_code]['id']
            full_name = fake.name()
            email = f"{emp_code.lower()}@smartoffice.local"
            phone = fake.phone_number()[:50]
            hire_date = fake.date_between(start_date='-3y', end_date='today')
            
            employees_to_insert.append((
                emp_code, full_name, email, phone, dept_id, pos_id, office_id, hire_date
            ))
            emp_counter += 1

    # Insert employees
    insert_query = """
        INSERT INTO hr.employees (employee_code, full_name, email, phone, department_id, position_id, office_id, hire_date)
        VALUES %s RETURNING employee_id, employee_code, department_id, position_id;
    """
    psycopg2.extras.execute_values(cur, insert_query, employees_to_insert, page_size=100)
    print(f"Generated {len(employees_to_insert)} employees.")

def assign_managers(cur):
    print("Assigning Managers to Hierarchy...")
    
    cur.execute("""
        SELECT e.employee_id, e.department_id, p.level 
        FROM hr.employees e
        JOIN hr.positions p ON e.position_id = p.position_id
    """)
    employees = cur.fetchall()
    
    managers_by_dept = {}
    ceo_id = None
    
    for emp_id, dept_id, level in employees:
        if level == 'EXECUTIVE':
            cur.execute("SELECT employee_id FROM hr.employees e JOIN hr.positions p ON e.position_id = p.position_id WHERE p.position_code = 'CEO'")
            ceo_row = cur.fetchone()
            ceo_id = ceo_row[0] if ceo_row else None
            
        elif level == 'MANAGER':
            managers_by_dept[dept_id] = emp_id

    # Assign staff to their department managers
    for emp_id, dept_id, level in employees:
        if level == 'STAFF':
            mgr_id = managers_by_dept.get(dept_id, ceo_id) # fallback to CEO
            if mgr_id:
                cur.execute("UPDATE hr.employees SET manager_id = %s WHERE employee_id = %s", (mgr_id, emp_id))
        elif level == 'MANAGER':
            if ceo_id:
                cur.execute("UPDATE hr.employees SET manager_id = %s WHERE employee_id = %s", (ceo_id, emp_id))
        elif level == 'EXECUTIVE' and emp_id != ceo_id:
            if ceo_id:
                cur.execute("UPDATE hr.employees SET manager_id = %s WHERE employee_id = %s", (ceo_id, emp_id))

    # Update department's manager_id
    for dept_id, mgr_id in managers_by_dept.items():
        cur.execute("UPDATE hr.departments SET manager_id = %s WHERE department_id = %s", (mgr_id, dept_id))
        
    if ceo_id:
        cur.execute("UPDATE hr.departments SET manager_id = %s WHERE department_code = 'EXEC'", (ceo_id,))

    print("Managers assigned successfully.")

def generate_rooms(cur, offices):
    print("Generating Meeting Rooms...")
    rooms_to_insert = []
    
    for office_code, count in ROOM_COUNTS.items():
        office_id = offices[office_code]
        for i in range(1, count + 1):
            room_code = f"{office_code}-MR-{i:03d}"
            room_name = f"Meeting Room {i} ({office_code})"
            floor = str(random.randint(1, 5))
            capacity = random.choices(ROOM_CAPACITIES, weights=ROOM_CAPACITY_WEIGHTS, k=1)[0]
            
            has_projector = random.choice([True, False])
            has_video_conference = random.choice([True, False]) if capacity >= 6 else False
            has_whiteboard = True
            
            rooms_to_insert.append((
                room_code, room_name, office_id, floor, capacity, has_projector, has_video_conference, has_whiteboard
            ))
            
    insert_query = """
        INSERT INTO meeting.rooms (room_code, room_name, office_id, floor, capacity, has_projector, has_video_conference, has_whiteboard)
        VALUES %s
    """
    psycopg2.extras.execute_values(cur, insert_query, rooms_to_insert)
    print(f"Generated {len(rooms_to_insert)} meeting rooms.")

def generate_doors(cur, offices):
    print("Generating Access Doors...")
    doors_to_insert = []
    
    for office_code, office_id in offices.items():
        door_configs = [
            ('ENTRY', 2),
            ('EXIT', 2),
            ('ROOM', 4),
            ('RESTRICTED', 1)
        ]
        
        for door_type, count in door_configs:
            for i in range(1, count + 1):
                door_code = f"{office_code}-{door_type}-{i:02d}"
                door_name = f"{door_type.capitalize()} Door {i}"
                floor = str(random.randint(1, 5)) if door_type == 'ROOM' else '1'
                zone = f"Zone {random.choice(['A', 'B', 'C'])}"
                
                doors_to_insert.append((
                    door_code, door_name, office_id, floor, zone, door_type
                ))
                
    insert_query = """
        INSERT INTO access.doors (door_code, door_name, office_id, floor, zone, door_type)
        VALUES %s
    """
    psycopg2.extras.execute_values(cur, insert_query, doors_to_insert)
    print(f"Generated {len(doors_to_insert)} doors.")

def generate_iot_devices(cur, offices):
    print("Generating IoT Devices...")
    
    cur.execute("SELECT room_id, office_id FROM meeting.rooms")
    rooms = cur.fetchall()
    
    office_rooms = {office_id: [] for office_id in offices.values()}
    for r_id, o_id in rooms:
        office_rooms[o_id].append(r_id)
        
    devices_to_insert = []
    device_counter = 1
    
    device_types = ['TEMPERATURE_SENSOR', 'HUMIDITY_SENSOR', 'CO2_SENSOR', 'OCCUPANCY_SENSOR', 'MULTI_SENSOR']
    
    for office_code, office_id in offices.items():
        # Room devices
        for r_id in office_rooms[office_id]:
            devices_to_insert.append((
                f"DEV-{device_counter:05d}", f"Room Occupancy {office_code}", "OCCUPANCY_SENSOR", office_id, r_id
            ))
            device_counter += 1
            if random.random() > 0.5:
                devices_to_insert.append((
                    f"DEV-{device_counter:05d}", f"Room Environment {office_code}", "MULTI_SENSOR", office_id, r_id
                ))
                device_counter += 1
                
        # Lobby/hallway devices (no room_id)
        for _ in range(10):
            dtype = random.choice(device_types)
            devices_to_insert.append((
                f"DEV-{device_counter:05d}", f"Hallway {dtype} {office_code}", dtype, office_id, None
            ))
            device_counter += 1
            
    insert_query = """
        INSERT INTO iot.devices (device_code, device_name, device_type, office_id, room_id)
        VALUES %s
    """
    psycopg2.extras.execute_values(cur, insert_query, devices_to_insert)
    print(f"Generated {len(devices_to_insert)} IoT devices.")

def clear_existing_data(cur):
    print("Clearing existing data...")
    cur.execute("UPDATE hr.departments SET manager_id = NULL")
    tables = [
        "iot.device_events", "iot.devices",
        "signing.signing_requests", "signing.documents",
        "meeting.bookings", "meeting.rooms",
        "access.access_events", "access.doors",
        "hr.employees"
    ]
    for tbl in tables:
        cur.execute(f"DELETE FROM {tbl}")

def main():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            clear_existing_data(cur)
            departments, positions, offices = fetch_reference_data(cur)
            
            generate_employees(cur, departments, positions, offices)
            assign_managers(cur)
            
            generate_rooms(cur, offices)
            generate_doors(cur, offices)
            generate_iot_devices(cur, offices)
            
        conn.commit()
        print("Master data generated successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error during data generation: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
