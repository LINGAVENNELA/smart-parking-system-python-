import time

MAX_CAPACITY = 25

class Vehicle:
    def __init__(self, vid, vtype, vip=False):
        self.id = vid
        self.type = vtype
        self.vip = vip
        self.park_time = time.time()

    def parked_duration_str(self):
        secs = int(time.time() - self.park_time)
        return f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}:{secs % 60:02d}"


class ParkingLot:
    def __init__(self, vtype):
        self.type = vtype
        self.capacity = MAX_CAPACITY
        self.slots = []
        self.waiting_queue = []

    def park_vehicle(self, vehicle):
        if len(self.slots) < self.capacity:
            self.slots.append(vehicle)
            return True, "✅ Vehicle Parked"
        else:
            self.waiting_queue.append(vehicle)
            return False, "🕓 Parking Full: Added to Waiting Queue"

    def remove_vehicle(self, vehicle_id):
        for i, v in enumerate(self.slots):
            if v.id == vehicle_id:
                self.slots.pop(i)
                if self.waiting_queue:
                    next_v = self.waiting_queue.pop(0)
                    self.slots.append(next_v)
                return True, "🚗 Vehicle Removed from Parking"
        for i, v in enumerate(self.waiting_queue):
            if v.id == vehicle_id:
                self.waiting_queue.pop(i)
                return True, "⏳ Vehicle Removed from Waiting Queue"
        return False, "❌ Vehicle Not Found"

    def list_vehicles(self):
        print(f"\n== {self.type} Parking Lot ==")
        print(f"Capacity: {len(self.slots)}/{self.capacity}")
        if self.slots:
            print("\n🚘 Parked Vehicles:")
            for v in self.slots:
                status = "VIP" if v.vip else "Normal"
                print(f"  - ID: {v.id}, {status}, Time: {v.parked_duration_str()}")
        else:
            print("No vehicles currently parked.")
        if self.waiting_queue:
            print("\n🕒 Waiting Queue:")
            for v in self.waiting_queue:
                status = "VIP" if v.vip else "Normal"
                print(f"  - ID: {v.id}, {status}, Waiting: {v.parked_duration_str()}")
        print("")


class ParkingSystem:
    def __init__(self):
        self.lots = {
            "Two-Wheeler": ParkingLot("Two-Wheeler"),
            "Four-Wheeler": ParkingLot("Four-Wheeler"),
            "Heavy Vehicle": ParkingLot("Heavy Vehicle"),
        }

    def add_vehicle(self, vid, vtype, vip):
        if vtype not in self.lots:
            return False, "❌ Invalid Vehicle Type"
        vehicle = Vehicle(vid, vtype, vip)
        return self.lots[vtype].park_vehicle(vehicle)

    def remove_vehicle(self, vid):
        for lot in self.lots.values():
            success, msg = lot.remove_vehicle(vid)
            if success:
                return True, msg
        return False, "❌ Vehicle Not Found in Any Lot"

    def show_status(self):
        for lot in self.lots.values():
            lot.list_vehicles()


def run_cli():
    system = ParkingSystem()
    print("🅿️  Welcome to the Smart Parking System CLI")
    while True:
        print("\nMenu:")
        print("1. 🚙 Add Vehicle")
        print("2. ❌ Remove Vehicle")
        print("3. 📊 Show Parking Status")
        print("4. 🚪 Exit")

        choice = input("Enter choice (1-4): ").strip()
        if choice == '1':
            vid = input("Enter Vehicle ID: ").strip()
            print("Select Vehicle Type:")
            print("1. Two-Wheeler\n2. Four-Wheeler\n3. Heavy Vehicle")
            vt_choice = input("Choice: ").strip()
            vtype = {"1": "Two-Wheeler", "2": "Four-Wheeler", "3": "Heavy Vehicle"}.get(vt_choice)
            if not vtype:
                print("❌ Invalid Type Selected.")
                continue
            vip_input = input("Is this a VIP vehicle? (y/n): ").strip().lower()
            vip = vip_input == 'y'
            success, msg = system.add_vehicle(vid, vtype, vip)
            print(msg)

        elif choice == '2':
            vid = input("Enter Vehicle ID to remove: ").strip()
            success, msg = system.remove_vehicle(vid)
            print(msg)

        elif choice == '3':
            system.show_status()

        elif choice == '4':
            print("👋 Exiting Smart Parking CLI. Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


# Entry point if running directly
if __name__ == "__main__":
    run_cli()
