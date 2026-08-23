import time
import argparse
import logging
import sys
import random

# Ensure root dir in path if executed directly
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from source.generator import config, db
from source.generator.live.clock import SimulationClock
from source.generator.live.access import AccessSimulator
from source.generator.live.iot import IoTSimulator
from source.generator.live.meeting import MeetingSimulator
from source.generator.live.signing import SigningSimulator
from source.generator.live.employee import EmployeeSimulator
from source.generator.live.delete_demo import emit_delete_demo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_live_generator(args):
    clock = SimulationClock(config.SIMULATION_START_TIME, config.SIMULATION_SPEED)
    
    retry_delays = [1, 2, 5, 10, 30]
    conn = None
    for delay in retry_delays:
        try:
            conn = db.get_connection()
            logger.info("Connected to database.")
            break
        except Exception as e:
            logger.error("Failed to connect to database: %s. Retrying in %ss...", e, delay)
            time.sleep(delay)
            
    if not conn:
        logger.error("Could not establish database connection. Exiting.")
        sys.exit(1)
        
    master_data = db.fetch_master_data(conn)
    
    access_sim = AccessSimulator(master_data)
    iot_sim = IoTSimulator(master_data)
    meeting_sim = MeetingSimulator(master_data)
    signing_sim = SigningSimulator(master_data)
    emp_sim = EmployeeSimulator(master_data)
    
    if args.emit_delete_demo or config.ENABLE_DELETE_DEMO:
        emit_delete_demo(conn, master_data['offices'][0])
        
    start_real_time = time.time()
    
    try:
        while True:
            sim_time = clock.tick(config.LIVE_GENERATOR_TICK_SECONDS)
            
            try:
                if random.random() < config.ACCESS_EVENT_RATE:
                    access_sim.generate_event(conn, sim_time)
            except Exception as e:
                logger.exception("Access event failed")
                
            try:
                if random.random() < config.IOT_EVENT_RATE:
                    iot_sim.generate_event(conn, sim_time)
            except Exception as e:
                logger.exception("IoT event failed")
                
            try:
                if random.random() < config.BOOKING_CREATE_RATE:
                    meeting_sim.create_booking(conn, sim_time)
                if random.random() < config.BOOKING_UPDATE_RATE:
                    meeting_sim.update_booking(conn, sim_time)
            except Exception as e:
                logger.exception("Booking event failed")
                
            try:
                if random.random() < config.DOCUMENT_CREATE_RATE:
                    signing_sim.create_document(conn, sim_time)
                if random.random() < config.SIGNING_UPDATE_RATE:
                    signing_sim.update_signing(conn, sim_time)
            except Exception as e:
                logger.exception("Signing event failed")
                
            try:
                if random.random() < config.EMPLOYEE_UPDATE_RATE:
                    emp_sim.generate_event(conn, sim_time)
            except Exception as e:
                logger.exception("Employee update failed")
                
            if args.once:
                logger.info("Completed single tick (--once). Exiting.")
                break
                
            if args.duration and (time.time() - start_real_time) >= args.duration:
                logger.info("Reached duration of %ss. Exiting.", args.duration)
                break
                
            time.sleep(config.LIVE_GENERATOR_TICK_SECONDS)
    except KeyboardInterrupt:
        logger.info("Stopping live generator")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Smart Office Data Generator")
    parser.add_argument("--once", action="store_true", help="Run one tick and exit")
    parser.add_argument("--duration", type=int, help="Run for X real seconds")
    parser.add_argument("--emit-delete-demo", action="store_true", help="Emit a DELETE event for CDC testing")
    args = parser.parse_args()
    
    run_live_generator(args)
