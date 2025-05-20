# MOCK controller.py - KHÔNG kết nối Arduino, chỉ in ra màn hình

def led(state):
    print(f"[MOCK] LED {'ON' if state else 'OFF'}")

def tv(state):
    print(f"[MOCK] TV {'ON' if state else 'OFF'}")

def fan(state):
    print(f"[MOCK] Quạt {'ON' if state else 'OFF'}")

def stove(state):
    print(f"[MOCK] Bếp {'ON' if state else 'OFF'}")

def ac(state):
    print(f"[MOCK] Điều hòa {'ON' if state else 'OFF'}")