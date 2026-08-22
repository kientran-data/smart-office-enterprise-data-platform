import random
from datetime import timedelta, datetime

def date_range(start_date, end_date):
    """Generator for iterating through dates."""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
        
def get_gaussian_time(base_date, mu_hour, sigma_hour):
    """Returns a datetime for a given date centered around a target hour."""
    hours = random.gauss(mu_hour, sigma_hour)
    # Clamp between 0 and 23.99
    hours = max(0.0, min(23.9999, hours))
    minutes = int((hours % 1) * 60)
    seconds = int((((hours % 1) * 60) % 1) * 60)
    return datetime.combine(base_date, datetime.min.time()) + timedelta(hours=int(hours), minutes=minutes, seconds=seconds)
