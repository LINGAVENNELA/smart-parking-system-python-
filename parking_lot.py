import time
from core.models.vehicle import Vehicle

class ParkingLot:
    def __init__(self):
        self.capacity = 25
        # Separate stacks for each vehicle type
        self.two_wheeler_stack = []
        self.four_wheeler_stack = []
        self.heavy_vehicle_stack = []

    def park_vehicle(self, vehicle: Vehicle):
        stack = self.get_stack(vehicle.type)
        if len(stack) < self.capacity:
            vehicle.entry_time = time.time()
            stack.append(vehicle)
            return True
        else:
            return False

    def remove_vehicle(self, vehicle_number: str):
        for stack in [self.two_wheeler_stack, self.four_wheeler_stack, self.heavy_vehicle_stack]:
            idx = self.find_vehicle_in_stack(stack, vehicle_number)
            if idx != -1:
                vehicle = stack.pop(idx)
                return vehicle
        return None

    def find_vehicle_in_stack(self, stack, vehicle_number):
        for i in range(len(stack)-1, -1, -1):
            if stack[i].number == vehicle_number:
                return i
        return -1

    def get_stack(self, vehicle_type):
        if vehicle_type == "Two-Wheeler":
            return self.two_wheeler_stack
        elif vehicle_type == "Four-Wheeler":
            return self.four_wheeler_stack
        else:
            return self.heavy_vehicle_stack

    def get_all_vehicles(self):
        # return all parked vehicles in order (any order you like)
        return self.two_wheeler_stack + self.four_wheeler_stack + self.heavy_vehicle_stack

    def get_status(self):
        return {
            "Two-Wheeler": len(self.two_wheeler_stack),
            "Four-Wheeler": len(self.four_wheeler_stack),
            "Heavy Vehicle": len(self.heavy_vehicle_stack)
        }

def export_logs(parking_lot, waiting_queues, filename="parking_log.csv"):
    import csv
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Parked Vehicles"])
        writer.writerow(["Type", "Number", "VIP", "Entry Time"])
        for vtype, stack in zip(
            ["Two-Wheeler", "Four-Wheeler", "Heavy Vehicle"],
            [parking_lot.two_wheeler_stack, parking_lot.four_wheeler_stack, parking_lot.heavy_vehicle_stack]
        ):
            for v in stack:
                et = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.entry_time)) if v.entry_time else "N/A"
                writer.writerow([vtype, v.number, "Yes" if v.is_vip else "No", et])
        writer.writerow([])
        writer.writerow(["Waiting Queues"])
        for vtype, queue in waiting_queues.items():
            writer.writerow([f"{vtype} Queue"])
            writer.writerow(["Number", "VIP", "Arrival Time"])
            for v in queue:
                at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.entry_time)) if v.entry_time else "N/A"
                writer.writerow([v.number, "Yes" if v.is_vip else "No", at])
            writer.writerow([])

