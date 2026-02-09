import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import time
from gui.qr_utils import generate_qr, decode_qr
from gui.timer_utils import schedule_removal, cancel_removal

# Constants for pastel colors per vehicle type
PASTEL_COLORS = {
    "Two-Wheeler": "#b2dfdb",
    "Four-Wheeler": "#ffe0b2",
    "Heavy Vehicle": "#c5cae9"
}
VIP_HIGHLIGHT = "#fff9c4"
MAX_CAPACITY = 25

class Vehicle:
    def __init__(self, vid, vtype, vip=False):
        self.id = vid
        self.type = vtype
        self.vip = vip
        self.park_time = time.time()

    def parked_duration(self):
        return time.time() - self.park_time

    def parked_duration_str(self):
        secs = int(self.parked_duration())
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
            return True, "Parked"
        else:
            self.waiting_queue.append(vehicle)
            return False, "Added to waiting queue"

    def remove_vehicle(self, vehicle_id):
        for i, v in enumerate(self.slots):
            if v.id == vehicle_id:
                self.slots.pop(i)
                if self.waiting_queue:
                    next_v = self.waiting_queue.pop(0)
                    self.slots.append(next_v)
                return True, f"Removed {vehicle_id}"
        for i, v in enumerate(self.waiting_queue):
            if v.id == vehicle_id:
                self.waiting_queue.pop(i)
                return True, f"Removed {vehicle_id} from waiting"
        return False, "Vehicle not found"

    def get_parked_vehicles(self):
        return self.slots

    def get_waiting_vehicles(self):
        return self.waiting_queue

class ParkingSystem:
    def __init__(self):
        self.lots = {
            "Two-Wheeler": ParkingLot("Two-Wheeler"),
            "Four-Wheeler": ParkingLot("Four-Wheeler"),
            "Heavy Vehicle": ParkingLot("Heavy Vehicle"),
        }
        self.logs = []

    def add_vehicle(self, vid, vtype, vip):
        if vtype not in self.lots:
            return False, "Invalid vehicle type"
        vehicle = Vehicle(vid, vtype, vip)
        parked, msg = self.lots[vtype].park_vehicle(vehicle)
        self.logs.append((datetime.datetime.now(), vid, vtype, "VIP" if vip else "Normal", msg))
        return parked, msg

    def remove_vehicle(self, vid):
        for lot in self.lots.values():
            success, msg = lot.remove_vehicle(vid)
            if success:
                self.logs.append((datetime.datetime.now(), vid, lot.type, "Removed", msg))
                return True, msg
        return False, "Vehicle not found"

    def export_logs(self, filepath):
        try:
            with open(filepath, "w") as f:
                f.write("Timestamp,VehicleID,Type,Status,Message\n")
                for entry in self.logs:
                    ts, vid, vtype, status, msg = entry
                    f.write(f"{ts},{vid},{vtype},{status},{msg}\n")
            return True, "Logs exported successfully"
        except Exception as e:
            return False, str(e)

class ParkingLotGUI(tk.Tk):
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.title("Smart Parking System")
        self.geometry("800x900")
        self.configure(bg="#f0f4f8")
        style = ttk.Style(self)
        style.theme_use("default")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        header = tk.Label(self.scrollable_frame, text="Smart Parking System", font=("Segoe UI", 24, "bold"), bg="#f0f4f8", fg="#1a3e5c")
        header.pack(pady=15)

        self.lot_frames = {}
        for vtype in self.system.lots:
            frame = ttk.LabelFrame(self.scrollable_frame, text=f"{vtype} Parking Lot (Capacity: {MAX_CAPACITY})", padding=15)
            frame.pack(padx=20, pady=12, fill="x")
            self.lot_frames[vtype] = frame
            self.create_parking_lot_ui(frame, vtype)

        ctrl_frame = ttk.Frame(self.scrollable_frame)
        ctrl_frame.pack(pady=20, fill="x")

        ttk.Label(ctrl_frame, text="Vehicle ID:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e", padx=8, pady=8)
        self.vehicle_id_entry = ttk.Entry(ctrl_frame, font=("Segoe UI", 11))
        self.vehicle_id_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(ctrl_frame, text="Vehicle Type:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e", padx=8, pady=8)
        self.vehicle_type_cb = ttk.Combobox(ctrl_frame, values=list(self.system.lots.keys()), state="readonly", font=("Segoe UI", 11))
        self.vehicle_type_cb.current(0)
        self.vehicle_type_cb.grid(row=1, column=1, padx=8, pady=8)

        self.vip_var = tk.BooleanVar()
        vip_cb = ttk.Checkbutton(ctrl_frame, text="VIP Vehicle", variable=self.vip_var)
        vip_cb.grid(row=2, column=1, sticky="w", padx=8, pady=8)

        ttk.Button(ctrl_frame, text="Add Vehicle", command=self.add_vehicle).grid(row=3, column=0, padx=10, pady=12)
        ttk.Button(ctrl_frame, text="Remove Vehicle", command=self.remove_vehicle).grid(row=3, column=1, padx=10, pady=12)
        ttk.Button(ctrl_frame, text="Export Logs", command=self.export_logs).grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(ctrl_frame, text="Scan QR to Exit", command=self.scan_qr_and_exit).grid(row=5, column=0, columnspan=2, pady=12)

        self.timer_label = ttk.Label(self.scrollable_frame, text="", font=("Segoe UI", 12))
        self.timer_label.pack(pady=10)

        self.update_ui()
        self.update_timer()

    def create_parking_lot_ui(self, parent_frame, vtype):
        color = PASTEL_COLORS.get(vtype, "#ddd")
        slots_frame = ttk.Frame(parent_frame)
        slots_frame.pack(fill="x", pady=8)
        slot_labels = []
        for i in range(MAX_CAPACITY):
            lbl = tk.Label(slots_frame, text=str(i + 1), relief="ridge", width=6, height=4, bg=color, borderwidth=2)
            lbl.grid(row=i // 10, column=i % 10, padx=5, pady=5)
            slot_labels.append(lbl)
        parent_frame.slot_labels = slot_labels
        waiting_frame = ttk.LabelFrame(parent_frame, text="Waiting Queue")
        waiting_frame.pack(fill="x", pady=8)
        waiting_labels = []
        for i in range(10):
            lbl = tk.Label(waiting_frame, text="-", relief="groove", width=10, height=2, bg="#eee", borderwidth=1)
            lbl.grid(row=0, column=i, padx=3, pady=3)
            waiting_labels.append(lbl)
        parent_frame.waiting_labels = waiting_labels

    def update_ui(self):
        for vtype, frame in self.lot_frames.items():
            lot = self.system.lots[vtype]
            for idx, lbl in enumerate(frame.slot_labels):
                if idx < len(lot.slots):
                    v = lot.slots[idx]
                    lbl.config(text=f"{v.id}\n{v.parked_duration_str()}", bg=VIP_HIGHLIGHT if v.vip else PASTEL_COLORS[vtype])
                else:
                    lbl.config(text=str(idx + 1), bg=PASTEL_COLORS[vtype])
            for idx, lbl in enumerate(frame.waiting_labels):
                if idx < len(lot.waiting_queue):
                    v = lot.waiting_queue[idx]
                    lbl.config(text=f"{v.id}\n{v.parked_duration_str()}", bg=VIP_HIGHLIGHT if v.vip else "#ddd")
                else:
                    lbl.config(text="-", bg="#eee")
        self.after(1000, self.update_ui)

    def update_timer(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timer_label.config(text=f"Current Time: {now}")
        self.after(1000, self.update_timer)

    def add_vehicle(self):
        vid = self.vehicle_id_entry.get().strip()
        vtype = self.vehicle_type_cb.get()
        vip = self.vip_var.get()
        if not vid:
            messagebox.showwarning("Input Error", "Please enter a vehicle ID")
            return
        success, msg = self.system.add_vehicle(vid, vtype, vip)
        messagebox.showinfo("Add Vehicle", msg)
        if success:
            qr_path = generate_qr(vid, datetime.datetime.now().isoformat(), vtype)
            schedule_removal(vid, 1800, lambda v=vid: self.system.remove_vehicle(v))
            self.vehicle_id_entry.delete(0, tk.END)
        self.update_ui()

    def remove_vehicle(self):
        vid = self.vehicle_id_entry.get().strip()
        if not vid:
            messagebox.showwarning("Input Error", "Please enter a vehicle ID")
            return
        cancel_removal(vid)
        success, msg = self.system.remove_vehicle(vid)
        messagebox.showinfo("Remove Vehicle", msg)
        if success:
            self.vehicle_id_entry.delete(0, tk.END)
        self.update_ui()

    def export_logs(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")])
        if not fpath:
            return
        success, msg = self.system.export_logs(fpath)
        if success:
            messagebox.showinfo("Export Logs", msg)
        else:
            messagebox.showerror("Export Logs", msg)

    def scan_qr_and_exit(self):
        file_path = filedialog.askopenfilename(title="Select QR Code Image")
        if file_path:
            decoded = decode_qr(file_path)
            if decoded:
                vehicle_id, entry_time, vehicle_type = decoded
                cancel_removal(vehicle_id)
                success, msg = self.system.remove_vehicle(vehicle_id)
                self.update_ui()
                messagebox.showinfo("Exit Success", f"{msg}")
            else:
                messagebox.showerror("Invalid QR", "Could not decode QR code.")


def main():
    system = ParkingSystem()
    app = ParkingLotGUI(system)
    app.mainloop()

if __name__ == "__main__":
    main()
# qr_utils.py

import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

def generate_qr(data, filename):
    qr = qrcode.make(data)
    qr.save(filename)

def decode_qr(image_path):
    img = Image.open(image_path)
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None
