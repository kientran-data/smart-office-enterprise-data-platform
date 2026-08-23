from datetime import datetime, timedelta


class SimulationClock:
    def __init__(
        self,
        start_time: datetime,
        speed: int = 60,
    ):
        self.current_time = start_time
        self.speed = speed

    def tick(self, real_seconds: float = 1):
        simulated_seconds = (
            real_seconds * self.speed
        )

        self.current_time += timedelta(
            seconds=simulated_seconds
        )

        return self.current_time