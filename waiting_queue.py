from collections import deque

class WaitingQueue:
    def __init__(self):
        self.queue = deque()

    def add_vehicle(self, vehicle):
        if vehicle.is_vip:
            self.queue.appendleft(vehicle)
        else:
            self.queue.append(vehicle)

    def next_vehicle(self):
        return self.queue.popleft() if self.queue else None

    def get_all(self):
        return list(self.queue)

    def size(self):
        return len(self.queue)
