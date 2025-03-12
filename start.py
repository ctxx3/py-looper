import sys, os
# Add project root to sys.path so modules can be imported locally
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import threading
import time
from looper.loopstation import LoopStation

def main():
    loop_station = LoopStation(bpm=120, beats_per_loop=8)
    
    # Start keyboard control thread with try/except handling
    try:
        from looper import keyboard_control
        kb_thread = threading.Thread(target=keyboard_control.keyboard_control, args=(loop_station,))
        kb_thread.daemon = True
        kb_thread.start()
        print("Keyboard control enabled")
    except ImportError:
        print("keyboard_control not available")
    
    # Try to start GPIO control if available
    try:
        from looper import gpio_control
        gpio_thread = threading.Thread(target=gpio_control.gpio_control, args=(loop_station,))
        gpio_thread.daemon = True
        gpio_thread.start()
        print("GPIO control enabled")
    except ImportError:
        print("gpio_control not available")
    
    while loop_station.is_running:
        time.sleep(0.1)

if __name__ == "__main__":
    main()