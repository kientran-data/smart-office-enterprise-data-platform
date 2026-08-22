import random
import logging

logger = logging.getLogger(__name__)

class EmployeeSimulator:
    def __init__(self, master_data):
        self.staff_employees = [e for e in master_data['employees'] if e['employment_type'] in ['FULL_TIME', 'PART_TIME', 'CONTRACT']]
        
    def generate_event(self, conn, simulation_time):
        if not self.staff_employees: return
        emp = random.choice(self.staff_employees)
        emp_id = emp['id']
        
        action = random.choices(['DEPARTMENT', 'POSITION', 'TERMINATE'], weights=[0.4, 0.4, 0.2])[0]
        
        try:
            with conn:
                with conn.cursor() as cur:
                    if action == 'TERMINATE':
                        cur.execute("UPDATE hr.employees SET status = 'TERMINATED', termination_date = %s WHERE employee_id = %s", (simulation_time.date(), emp_id))
                        self.staff_employees.remove(emp)
                    elif action == 'DEPARTMENT':
                        cur.execute("SELECT department_id FROM hr.departments WHERE department_id != (SELECT department_id FROM hr.employees WHERE employee_id = %s) ORDER BY RANDOM() LIMIT 1", (emp_id,))
                        row = cur.fetchone()
                        if row:
                            cur.execute("UPDATE hr.employees SET department_id = %s WHERE employee_id = %s", (row[0], emp_id))
                    elif action == 'POSITION':
                        cur.execute("SELECT position_id FROM hr.positions WHERE position_id != (SELECT position_id FROM hr.employees WHERE employee_id = %s) AND level = 'STAFF' ORDER BY RANDOM() LIMIT 1", (emp_id,))
                        row = cur.fetchone()
                        if row:
                            cur.execute("UPDATE hr.employees SET position_id = %s WHERE employee_id = %s", (row[0], emp_id))
            logger.info("EMPLOYEE employee=%s action=%s", emp_id, action)
        except Exception as e:
            logger.error("Failed employee update: %s", e)
