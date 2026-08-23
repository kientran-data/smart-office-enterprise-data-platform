import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from zoneinfo import ZoneInfo

from source.generator.live.clock import SimulationClock


clock = SimulationClock(
    start_time=datetime(
        2026,
        8,
        22,
        7,
        0,
        tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"),
    ),
    speed=60,
)

for _ in range(5):
    print(clock.tick())