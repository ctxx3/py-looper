import sys
import os
import threading
import time
from looper.loopstation import LoopStation

def add_project_root_to_path():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def start_control_thread(label, control_func, loop_station):
    try:
        thread = threading.Thread(target=control_func, args=(loop_station,))
        thread.daemon = True
        thread.start()
        print(f"{label} enabled")
    except Exception as e:
        print(f"Error starting {label.lower()}:", e)

def main():
    add_project_root_to_path()
    loop_station = LoopStation(bpm=120, beats_per_loop=8)
    
    # Keyboard control
    if os.name != 'nt' and os.geteuid() != 0:
        print("Keyboard control requires root privileges; skipping")
    else:
        try:
            from looper import keyboard_control
            start_control_thread("Keyboard control", keyboard_control.keyboard_control, loop_station)
        except ImportError:
            print("keyboard_control not available")
        except Exception as e:
            print("Error in keyboard control:", e)
    
    # GPIO control
    try:
        from looper import gpio_control
        start_control_thread("GPIO control", gpio_control.gpio_control, loop_station)
    except ImportError:
        print("gpio_control not available")
    
    # Web control
    try:
        from looper import web_control
        start_control_thread("Web control", web_control.web_control, loop_station)
    except ImportError:
        print("web_control not available")
    
    # Run until loop_station stops
    while loop_station.is_running:
        time.sleep(0.1)

if __name__ == "__main__":
    main()