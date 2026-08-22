import random
from datetime import timedelta, datetime
from tqdm import tqdm
from ..utils import date_range

def generate_signing_data(master_data, config):
    print("Generating Signing Data...")
    employees = master_data['employees']
    
    start_date = config.HISTORY_START_DATE
    end_date = config.HISTORY_END_DATE
    
    docs_to_insert = []
    reqs_to_insert = []
    
    doc_types = ['INTERNAL_REQUEST', 'PURCHASE_ORDER', 'CONTRACT', 'HR_DOCUMENT', 'POLICY']
    doc_weights = [0.35, 0.25, 0.15, 0.15, 0.10]
    
    turnarounds = [timedelta(minutes=30), timedelta(hours=2), timedelta(hours=6), timedelta(days=1), timedelta(days=3)]
    turnaround_weights = [0.30, 0.40, 0.15, 0.10, 0.05]
    
    doc_counter = 1
    
    for current_date in tqdm(list(date_range(start_date, end_date)), desc="Signing Docs"):
        num_docs = random.randint(0, 2) if current_date.weekday() >= 5 else random.randint(5, 15)
            
        for _ in range(num_docs):
            doc_code = f"DOC-{current_date.year}-{doc_counter:06d}"
            
            doc_type = random.choices(doc_types, weights=doc_weights, k=1)[0]
            
            valid_emps = [e for e in employees if e['hire_date'] <= current_date and (not e['termination_date'] or e['termination_date'] >= current_date)]
            if not valid_emps:
                continue
            
            creator = random.choice(valid_emps)
            created_at = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.uniform(9, 16))
            
            num_signers = random.randint(1, 3)
            signers = random.sample(valid_emps, num_signers)
            
            current_req_time = created_at + timedelta(minutes=5)
            
            doc_status = 'COMPLETED'
            doc_reqs = []
            
            for i, signer in enumerate(signers):
                turnaround = random.choices(turnarounds, weights=turnaround_weights, k=1)[0]
                signed_time = current_req_time + turnaround
                
                if random.random() < 0.05:
                    req_status = 'REJECTED'
                    doc_status = 'REJECTED'
                    doc_reqs.append((
                        doc_code, creator['id'], signer['id'], i+1, req_status, current_req_time, None, signed_time, current_req_time, signed_time
                    ))
                    break
                else:
                    req_status = 'SIGNED'
                    doc_reqs.append((
                        doc_code, creator['id'], signer['id'], i+1, req_status, current_req_time, signed_time, None, current_req_time, signed_time
                    ))
                    current_req_time = signed_time + timedelta(minutes=10)
            
            final_updated_at = doc_reqs[-1][9] if doc_reqs else created_at
            
            # Use doc_counter as ID because we RESTART IDENTITY in SQL reset
            doc_id = doc_counter
            docs_to_insert.append((
                doc_id, doc_code, f"{doc_type} {doc_code}", doc_type, creator['id'], doc_status, created_at, final_updated_at
            ))
            
            for req in doc_reqs:
                reqs_to_insert.append((
                    doc_id, req[1], req[2], req[3], req[4], req[5], req[6], req[7], req[8], req[9]
                ))
            
            doc_counter += 1
                
    return docs_to_insert, reqs_to_insert
