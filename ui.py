import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import json
import time
import uuid

# --- License Config ---
LICENSE_FILE = "license.json"
LICENSE_TIERS = {
    "Trial": 30 * 86400,
    "Basic": 90 * 86400,
    "Standard": 180 * 86400,
    "Pro": 270 * 86400,
    "Premium": 365 * 86400,
    "VIP Vinh Vien": None,  # Lifetime
    "test": 3600  # Test key: 1 hour
}

def get_machine_code():
    mac = uuid.getnode()
    mac_str = ':'.join(['{:02X}'.format((mac >> ele) & 0xff)
                        for ele in range(40, -1, -8)])
    return mac_str

def is_license_valid():
    if not os.path.exists(LICENSE_FILE):
        return False
    with open(LICENSE_FILE, "r") as file:
        license_info = json.load(file)
    license_type = license_info.get("license_type")
    registered_time = license_info.get("registered_time")
    if license_type not in LICENSE_TIERS:
        return False
    if LICENSE_TIERS[license_type] is None:
        return True  # Lifetime
    now = int(time.time())
    expiration = registered_time + LICENSE_TIERS[license_type]
    return now < expiration

def remaining_days():
    if not os.path.exists(LICENSE_FILE):
        return 0
    with open(LICENSE_FILE, "r") as file:
        license_info = json.load(file)
    license_type = license_info.get("license_type")
    if license_type not in LICENSE_TIERS:
        return 0
    if LICENSE_TIERS[license_type] is None:
        return "∞"
    now = int(time.time())
    expiration = license_info.get("registered_time") + LICENSE_TIERS[license_type]
    remaining_sec = expiration - now
    if license_type == "test":
        hours_left = remaining_sec // 3600
        minutes_left = (remaining_sec % 3600) // 60
        if hours_left < 0:
            return 0
        return f"{hours_left}h {minutes_left}m"
    remaining = remaining_sec // 86400
    return max(0, remaining)

def save_license(license_type):
    data = {
        "license_type": license_type,
        "registered_time": int(time.time()),
        "machine_code": get_machine_code()
    }
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

COMPANY_NAME = "CÔNG TY TNHH TRUYỀN THÔNG CÔNG NGHỆ, DU LỊCH VÀ GIÁO DỤC HOÀNG HẢI (HCTTE CO., LTD)"
COMPANY_ADDRESS = "Địa chỉ: 14-15A, Tầng 7, Tòa nhà Charmvit Tower, 117 Trần Duy Hưng, Trung Hòa, Cầu Giấy, Hà Nội"

class ToggleSwitch(tk.Frame):
    def __init__(self, parent, command=None, bg="#0063EC"):
        super().__init__(parent, bg=bg)
        self.state = False
        self.command = command if command else lambda _: None
        self.canvas = tk.Canvas(self, width=40, height=20, bg=bg, highlightthickness=0)
        self.rect = self.canvas.create_rectangle(0, 0, 40, 20, fill="#CCCCCC", outline="")
        self.circle = self.canvas.create_oval(2, 2, 18, 18, fill="white")
        self.canvas.bind("<Button-1>", self.toggle)
        self.canvas.pack()
    def toggle(self, event=None):
        self.state = not self.state
        self.update_visual()
        if self.command:
            self.command(self.state)
    def set_state(self, state):
        self.state = state
        self.update_visual()
    def update_visual(self):
        if self.state:
            self.canvas.itemconfig(self.rect, fill="#0063EC")
            self.canvas.coords(self.circle, 22, 2, 38, 18)
        else:
            self.canvas.itemconfig(self.rect, fill="#CCCCCC")
            self.canvas.coords(self.circle, 2, 2, 18, 18)

def load_image(file_path, size=(40, 40)):
    try:
        if os.path.exists(file_path):
            img = Image.open(file_path).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        else:
            return None
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return None

class SmartHomeApp:
    def __init__(self, root, username="Quý khách", role="Khách hàng"):
        self.root = root
        self.username = username
        self.role = role
        self.root.title("Hệ Thống Điều Khiển Ngôi Nhà Thông Minh Bằng AI")
        self.root.geometry("900x650")
        self.light_theme = {
            "bg": "#FFFFFF", "fg": "#0000FF", "button_bg": "#FFFFFF", "button_fg": "#0000FF",
            "button_hover": "#EEEEEE", "highlight_button_bg": "#FFFFFF", "highlight_button_fg": "#0000FF",
            "navbar_bg": "#FFFFFF", "navbar_fg": "#0063EC", "frame_bg": "#FFFFFF", "frame_fg": "#0000FF",
            "error_fg": "#0000FF", "hero_fg": "#0000FF", "logo_text_fg": "#0000FF", "logo_bg": "#FFFFFF",
            "slider_trough": "#D3D3D3", "slider_thumb": "#4CAF50", "canvas_bg": "#FFFFFF",
        }
        self.current_theme = self.light_theme
        self.root.configure(bg=self.current_theme["bg"])
        # Device states
        self.led_status = "OFF"
        self.fan_status = "OFF"
        self.ac_status = "OFF"
        self.tv_status = "OFF"
        self.stove_status = "OFF"
        # Load icons
        self.icons = {
            "led": load_image("image/light.png", size=(40,40)),
            "fan": load_image("image/fan.png", size=(40,40)),
            "ac": load_image("image/ac.png", size=(40,40)),
            "tv": load_image("image/tv.png", size=(40,40)),
            "stove": load_image("image/stove.png", size=(40,40)),
        }
        self.license_label = None
        self.license_frame = None
        self.license_entry = None
        self.license_machine_label = None
        self.license_msg_label = None
        self.setup_ui()
        self.update_license_label_periodically()
        self.root.bind("<Delete>", lambda e: self.root.destroy())

    def setup_ui(self):
        self.setup_header()
        self.setup_main_frame()
        self.setup_left_pane()
        self.setup_right_pane()
        self.apply_theme()

    def setup_header(self):
        header = tk.Frame(self.root, bg=self.current_theme["navbar_bg"], height=50)
        header.pack(side=tk.TOP, fill=tk.X)

        welcome_label = tk.Label(header, text=f"Xin chào, {self.username} ({self.role})", font=("Helvetica", 12, "bold"), fg=self.current_theme["navbar_fg"], bg=self.current_theme["navbar_bg"])
        welcome_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.license_label = tk.Label(header, text="", font=("Helvetica", 11, "bold"), fg="#0063EC", bg=self.current_theme["navbar_bg"])
        self.license_label.pack(side=tk.LEFT, padx=20)

        self.license_frame = tk.Frame(header, bg=self.current_theme["navbar_bg"])
        self.license_machine_label = tk.Label(self.license_frame, text=f"Mã máy: {get_machine_code()}", font=("Helvetica", 11, "bold"), bg=self.current_theme["navbar_bg"], fg=self.current_theme["navbar_fg"])
        self.license_machine_label.grid(row=0, column=0, padx=2, pady=1, sticky="w")
        self.license_entry = tk.Entry(self.license_frame, width=10)
        self.license_entry.grid(row=0, column=1, padx=2, pady=1)
        tk.Button(self.license_frame, text="Kích hoạt", font=("Helvetica", 11, "bold"), command=self.activate_license, bg=self.current_theme["navbar_bg"], fg=self.current_theme["navbar_fg"]).grid(row=0, column=2, padx=2, pady=1)
        self.license_msg_label = tk.Label(self.license_frame, text="", font=("Helvetica", 9), fg="red", bg=self.current_theme["navbar_bg"])
        self.license_msg_label.grid(row=1, column=0, columnspan=3, pady=(2,0))
        self.license_frame.pack_forget()

        self.exit_button = tk.Button(header, text="Thoát", command=self.root.destroy, font=("Helvetica", 11, "bold"), bg=self.current_theme["navbar_bg"], fg=self.current_theme["navbar_fg"], relief=tk.FLAT)
        self.exit_button.pack(side=tk.RIGHT, padx=5)

        self.license_btn = tk.Button(
            header,
            text="Quản lý License",
            font=("Helvetica", 11, "bold"),
            command=self.toggle_license_inline,
            bg=self.current_theme["navbar_bg"],
            fg=self.current_theme["navbar_fg"],
            borderwidth=0,
            highlightthickness=0
        )
        self.license_btn.pack(side=tk.RIGHT, padx=5)

    def toggle_license_inline(self):
        if self.license_frame.winfo_ismapped():
            self.license_frame.pack_forget()
        else:
            self.license_machine_label.config(text=f"Mã máy: {get_machine_code()}")
            self.license_msg_label.config(text="")
            self.license_entry.delete(0, tk.END)
            self.license_frame.pack(side=tk.RIGHT, padx=8)

    def activate_license(self):
        key = self.license_entry.get()
        if key in LICENSE_TIERS:
            save_license(key)
            self.update_license_label()
            self.license_msg_label.config(text=f"Kích hoạt thành công gói: {key}", fg="green")
            self.license_frame.pack_forget()
        else:
            self.license_msg_label.config(text="Mã không hợp lệ!", fg="red")

    def update_license_label(self):
        if os.path.exists(LICENSE_FILE):
            days = remaining_days()
            if days == "∞":
                text = "Thời hạn còn lại: Vĩnh viễn"
            elif isinstance(days, str) and "h" in days:
                text = f"Thời hạn còn lại: {days}"
            else:
                text = f"Thời hạn còn lại: {days} ngày"
        else:
            save_license("Trial")
            text = "Bắt đầu dùng thử: 30 ngày"
        if self.license_label:
            self.license_label.config(text=text)

    def update_license_label_periodically(self):
        self.update_license_label()
        self.root.after(1000, self.update_license_label_periodically)

    def setup_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def setup_left_pane(self):
        pane_width = 300
        self.left_pane = tk.Frame(self.main_frame, width=pane_width, bg=self.current_theme["bg"])
        self.left_pane.pack(side=tk.LEFT, fill=tk.Y)
        self.left_pane.pack_propagate(False)
        logo_container = tk.Frame(self.left_pane, bg=self.current_theme["bg"])
        logo_container.pack(expand=True)
        tk.Label(logo_container, text="CSHA-S1.0 'MÁY NÓI'", font=("Helvetica", 12, "bold"), fg=self.current_theme["logo_text_fg"], bg=self.current_theme["bg"]).pack(pady=(0, 0))
        logo_path = "image/logo.png"
        self.logo_label = tk.Label(logo_container, bg=self.current_theme["bg"])
        logo_photo = load_image(logo_path, size=(120, 120))
        if logo_photo:
            self.logo_label.configure(image=logo_photo)
            self.logo_label.image = logo_photo
        else:
            self.logo_label.configure(text="HOANGHAI TECHNOLOGY", fg=self.current_theme["logo_text_fg"], bg=self.current_theme["bg"], font=("Helvetica", 16, "bold"))
        self.logo_label.pack(pady=(0, 0))
        self.hoanghai_text_label = tk.Label(logo_container, text="HOANGHAI TECHNOLOGY", font=("Helvetica", 16, "bold"), fg=self.current_theme["logo_text_fg"], bg=self.current_theme["bg"])
        self.hoanghai_text_label.pack(pady=(0, 0))
        self.footer_label_left = tk.Label(self.left_pane, text=f"{COMPANY_NAME}\n{COMPANY_ADDRESS}", font=("Helvetica", 10), fg=self.current_theme["fg"], bg=self.current_theme["bg"], wraplength=pane_width - 30, justify=tk.LEFT)
        self.footer_label_left.pack(side=tk.BOTTOM, pady=10)

    def setup_right_pane(self):
        self.right_pane = tk.Frame(self.main_frame, bg=self.current_theme["bg"])
        self.right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        title_frame = tk.Frame(self.right_pane, bg=self.current_theme["bg"], height=50)
        title_frame.pack(fill=tk.X)
        self.title_label = tk.Label(title_frame, text="HỆ THỐNG ĐIỀU KHIẾN NGÔI NHÀ THÔNG MINH BẰNG AI", font=("Helvetica", 16, "bold"), fg=self.current_theme["hero_fg"], bg=self.current_theme["bg"])
        self.title_label.pack(pady=5)
        self.slogan_label = tk.Label(title_frame, text="GIẢI PHÁP CÔNG NGHỆ VIỆT", font=("Helvetica", 12), fg=self.current_theme["fg"], bg=self.current_theme["bg"])
        self.slogan_label.pack()
        self.dashboard_frame = tk.Frame(self.right_pane, bg=self.current_theme["frame_bg"], bd=2, relief=tk.GROOVE, padx=20, pady=10)
        self.dashboard_frame.pack(fill=tk.X, pady=5)
        self.dashboard_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.led_status_label = tk.Label(self.dashboard_frame, text=f"LED: {self.led_status}", font=("Helvetica", 11), fg=self.current_theme["frame_fg"], bg=self.current_theme["frame_bg"])
        self.led_status_label.grid(row=0, column=0, padx=15, pady=8, sticky='w')
        self.fan_status_label = tk.Label(self.dashboard_frame, text=f"Quạt: {self.fan_status}", font=("Helvetica", 11), fg=self.current_theme["frame_fg"], bg=self.current_theme["frame_bg"])
        self.fan_status_label.grid(row=0, column=1, padx=15, pady=8, sticky='w')
        self.ac_status_label = tk.Label(self.dashboard_frame, text=f"Điều hòa: {self.ac_status}", font=("Helvetica", 11), fg=self.current_theme["frame_fg"], bg=self.current_theme["frame_bg"])
        self.ac_status_label.grid(row=0, column=2, padx=15, pady=8, sticky='w')
        self.tv_status_label = tk.Label(self.dashboard_frame, text=f"TV: {self.tv_status}", font=("Helvetica", 11), fg=self.current_theme["frame_fg"], bg=self.current_theme["frame_bg"])
        self.tv_status_label.grid(row=0, column=3, padx=15, pady=8, sticky='w')
        self.stove_status_label = tk.Label(self.dashboard_frame, text=f"Bếp: {self.stove_status}", font=("Helvetica", 11), fg=self.current_theme["frame_fg"], bg=self.current_theme["frame_bg"])
        self.stove_status_label.grid(row=0, column=4, padx=15, pady=8, sticky='w')
        self.control_frame = tk.Frame(self.right_pane, bg=self.current_theme["frame_bg"], bd=2, relief=tk.GROOVE, padx=20, pady=10)
        self.control_frame.pack(fill=tk.X, pady=10)
        # LED Control
        self.led_frame = tk.Frame(self.control_frame, bg=self.current_theme["frame_bg"])
        self.led_frame.pack(fill=tk.X, pady=5)
        if self.icons["led"]:
            tk.Label(self.led_frame, image=self.icons["led"], bg=self.current_theme["frame_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Label(self.led_frame, text="LED", font=("Helvetica", 12, "bold"), bg=self.current_theme["frame_bg"], fg=self.current_theme["frame_fg"]).pack(side=tk.LEFT, padx=5)
        self.led_toggle = ToggleSwitch(self.led_frame, self.toggle_led, bg=self.current_theme["canvas_bg"])
        self.led_toggle.pack(side=tk.LEFT, padx=5)
        # Fan Control
        self.fan_frame = tk.Frame(self.control_frame, bg=self.current_theme["frame_bg"])
        self.fan_frame.pack(fill=tk.X, pady=5)
        if self.icons["fan"]:
            tk.Label(self.fan_frame, image=self.icons["fan"], bg=self.current_theme["frame_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Label(self.fan_frame, text="Quạt", font=("Helvetica", 12, "bold"), bg=self.current_theme["frame_bg"], fg=self.current_theme["frame_fg"]).pack(side=tk.LEFT, padx=5)
        self.fan_toggle = ToggleSwitch(self.fan_frame, self.toggle_fan, bg=self.current_theme["canvas_bg"])
        self.fan_toggle.pack(side=tk.LEFT, padx=5)
        # AC Control
        self.ac_frame = tk.Frame(self.control_frame, bg=self.current_theme["frame_bg"])
        self.ac_frame.pack(fill=tk.X, pady=5)
        if self.icons["ac"]:
            tk.Label(self.ac_frame, image=self.icons["ac"], bg=self.current_theme["frame_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Label(self.ac_frame, text="Điều hòa", font=("Helvetica", 12, "bold"), bg=self.current_theme["frame_bg"], fg=self.current_theme["frame_fg"]).pack(side=tk.LEFT, padx=5)
        self.ac_toggle = ToggleSwitch(self.ac_frame, self.toggle_ac, bg=self.current_theme["canvas_bg"])
        self.ac_toggle.pack(side=tk.LEFT, padx=5)
        # TV Control
        self.tv_frame = tk.Frame(self.control_frame, bg=self.current_theme["frame_bg"])
        self.tv_frame.pack(fill=tk.X, pady=5)
        if self.icons["tv"]:
            tk.Label(self.tv_frame, image=self.icons["tv"], bg=self.current_theme["frame_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Label(self.tv_frame, text="TV", font=("Helvetica", 12, "bold"), bg=self.current_theme["frame_bg"], fg=self.current_theme["frame_fg"]).pack(side=tk.LEFT, padx=5)
        self.tv_toggle = ToggleSwitch(self.tv_frame, self.toggle_tv, bg=self.current_theme["canvas_bg"])
        self.tv_toggle.pack(side=tk.LEFT, padx=5)
        # Stove Control
        self.stove_frame = tk.Frame(self.control_frame, bg=self.current_theme["frame_bg"])
        self.stove_frame.pack(fill=tk.X, pady=5)
        if self.icons["stove"]:
            tk.Label(self.stove_frame, image=self.icons["stove"], bg=self.current_theme["frame_bg"]).pack(side=tk.LEFT, padx=5)
        tk.Label(self.stove_frame, text="Bếp", font=("Helvetica", 12, "bold"), bg=self.current_theme["frame_bg"], fg=self.current_theme["frame_fg"]).pack(side=tk.LEFT, padx=5)
        self.stove_toggle = ToggleSwitch(self.stove_frame, self.toggle_stove, bg=self.current_theme["canvas_bg"])
        self.stove_toggle.pack(side=tk.LEFT, padx=5)
        self.notification = tk.Label(self.right_pane, text="Đang nghe...", font=("Helvetica", 12), fg=self.current_theme["error_fg"], bg=self.current_theme["bg"], pady=5)
        self.notification.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_led(self, state):
        self.led_status = "ON" if state else "OFF"
        self.led_status_label.config(text=f"LED: {self.led_status}")
        self.notification.config(text=f"LED: {self.led_status}")
    def toggle_fan(self, state):
        self.fan_status = "ON" if state else "OFF"
        self.fan_status_label.config(text=f"Quạt: {self.fan_status}")
        self.notification.config(text=f"Quạt: {self.fan_status}")
    def toggle_ac(self, state):
        self.ac_status = "ON" if state else "OFF"
        self.ac_status_label.config(text=f"Điều hòa: {self.ac_status}")
        self.notification.config(text=f"Điều hòa: {self.ac_status}")
    def toggle_tv(self, state):
        self.tv_status = "ON" if state else "OFF"
        self.tv_status_label.config(text=f"TV: {self.tv_status}")
        self.notification.config(text=f"TV: {self.tv_status}")
    def toggle_stove(self, state):
        self.stove_status = "ON" if state else "OFF"
        self.stove_status_label.config(text=f"Bếp: {self.stove_status}")
        self.notification.config(text=f"Bếp: {self.stove_status}")
    def apply_theme(self):
        theme = self.light_theme
        self.root.configure(bg=theme["bg"])
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.configure(bg=theme["bg"])
        if hasattr(self, 'right_pane') and self.right_pane:
            self.right_pane.configure(bg=theme["bg"])
        if hasattr(self, 'left_pane') and self.left_pane:
            self.left_pane.configure(bg=theme["bg"])

    # Thêm hàm để cập nhật trạng thái thiết bị từ bên ngoài (main.py)
    def set_device_states(self, led, tv, fan, stove, ac):
        self.led_toggle.set_state(led)
        self.tv_toggle.set_state(tv)
        self.fan_toggle.set_state(fan)
        self.stove_toggle.set_state(stove)
        self.ac_toggle.set_state(ac)
        self.toggle_led(led)
        self.toggle_tv(tv)
        self.toggle_fan(fan)
        self.toggle_stove(stove)
        self.toggle_ac(ac)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeApp(root)
    root.mainloop()