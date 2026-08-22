import random
import logging

logger = logging.getLogger(__name__)

class SigningSimulator:
    def __init__(self, master_data):
        self.employees = master_data['employees']
        self.doc_types = ['INTERNAL_REQUEST', 'PURCHASE_ORDER', 'CONTRACT', 'HR_DOCUMENT', 'POLICY']
        
    def create_document(self, conn, simulation_time):
        creator = random.choice(self.employees)
        doc_type = random.choice(self.doc_types)
        doc_code = f"DOC-LIVE-{simulation_time.strftime('%Y%m%d%H%M%S')}-{random.randint(10,99)}"
        title = f"Live {doc_type} {doc_code}"
        num_signers = random.randint(1, 3)
        signers = random.sample(self.employees, num_signers)
        
        try:
            with conn: # Context manager commits on success, rolls back on exception
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO signing.documents (document_code, title, document_type, creator_id, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, 'PENDING_SIGNATURE', %s, %s) RETURNING document_id
                    """, (doc_code, title, doc_type, creator['id'], simulation_time, simulation_time))
                    doc_id = cur.fetchone()[0]
                    
                    for i, signer in enumerate(signers):
                        cur.execute("""
                            INSERT INTO signing.signing_requests (document_id, requester_id, signer_id, signing_order, status, requested_at, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, 'PENDING', %s, %s, %s)
                        """, (doc_id, creator['id'], signer['id'], i+1, simulation_time, simulation_time, simulation_time))
            logger.info("SIGNING CREATE document=%s signers=%s", doc_id, num_signers)
        except Exception as e:
            logger.error("Failed to create live document: %s", e)

    def update_signing(self, conn, simulation_time):
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT request_id, document_id, signing_order FROM signing.signing_requests
                    WHERE status = 'PENDING'
                    ORDER BY requested_at ASC LIMIT 1
                """)
                row = cur.fetchone()
                if not row:
                    return
                req_id, doc_id, order = row
                
                req_status = 'SIGNED' if random.random() < 0.95 else 'REJECTED'
                
            with conn:
                with conn.cursor() as cur:
                    if req_status == 'SIGNED':
                        cur.execute("UPDATE signing.signing_requests SET status = 'SIGNED', signed_at = %s, updated_at = %s WHERE request_id = %s", (simulation_time, simulation_time, req_id))
                        
                        cur.execute("SELECT COUNT(*) FROM signing.signing_requests WHERE document_id = %s AND status != 'SIGNED'", (doc_id,))
                        if cur.fetchone()[0] == 0:
                            cur.execute("UPDATE signing.documents SET status = 'COMPLETED', updated_at = %s WHERE document_id = %s", (simulation_time, doc_id))
                            logger.info("SIGNING UPDATE document=%s COMPLETED", doc_id)
                    else:
                        cur.execute("UPDATE signing.signing_requests SET status = 'REJECTED', rejected_at = %s, updated_at = %s WHERE request_id = %s", (simulation_time, simulation_time, req_id))
                        cur.execute("UPDATE signing.documents SET status = 'REJECTED', updated_at = %s WHERE document_id = %s", (simulation_time, doc_id))
                        logger.info("SIGNING UPDATE document=%s REJECTED", doc_id)
            
            logger.info("SIGNING UPDATE request=%s -> %s", req_id, req_status)
        except Exception as e:
            logger.error("Failed to update live signing: %s", e)
