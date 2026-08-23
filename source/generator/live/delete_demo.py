import time
import logging

logger = logging.getLogger(__name__)

def emit_delete_demo(conn, office_id):
    logger.info("Starting DELETE demo CDC testing...")
    temporary_code = "TEMP-CDC-001"
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO access.doors (door_code, door_name, office_id, door_type, status)
                    VALUES (%s, 'CDC Temporary Door', %s, 'ENTRY', 'ACTIVE')
                    RETURNING door_id
                    """,
                    (temporary_code, office_id)
                )
                door_id = cur.fetchone()[0]
        logger.info("DELETE-DEMO Inserted temporary door=%s", door_id)
        
        time.sleep(2)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM access.doors WHERE door_id = %s", (door_id,))
        logger.info("DELETE-DEMO Deleted temporary door=%s", door_id)
    except Exception as e:
        logger.error("DELETE-DEMO failed: %s", e)
