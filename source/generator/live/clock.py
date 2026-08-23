from datetime import timedelta

class SimulationClock:
    def __init__(self, start_time, speed=60):
        self.current_time = start_time
        self.speed = speed

    def tick(self, real_seconds=1):
        self.current_time += timedelta(seconds=real_seconds * self.speed)
        return self.current_time
