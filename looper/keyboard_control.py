import time
import keyboard
import threading
from looper.loopstation import LoopStation

def keyboard_control(loop_station):
    print("\n=== PYTHON LOOP STATION ===")
    print(f"BPM: {loop_station.bpm}, Beats per loop: {loop_station.beats_per_loop}")
    print("\nKEYBOARD CONTROLS:\n1-3: Record tracks\nQ/W/E: Toggle tracks\nSPACE: Stop recording\n+/-: Adjust BPM\nM: Toggle metronome\nESC: Quit\n")
    key_actions = {
        '1': lambda: loop_station.start_recording(0),
        '2': lambda: loop_station.start_recording(1),
        '3': lambda: loop_station.start_recording(2),
        'q': lambda: loop_station.toggle_track(0),
        'w': lambda: loop_station.toggle_track(1),
        'e': lambda: loop_station.toggle_track(2),
        'space': lambda: loop_station.stop_recording(),
        '+': lambda: loop_station.change_bpm(loop_station.bpm + 5),
        '=': lambda: loop_station.change_bpm(loop_station.bpm + 5),
        '-': lambda: loop_station.change_bpm(max(60, loop_station.bpm - 5)),
        'm': lambda: loop_station.toggle_metronome(),
        'esc': lambda: (print("Shutting down..."), loop_station.shutdown())
    }
    while loop_station.is_running:
        time.sleep(0.05)
        for key, action in key_actions.items():
            if keyboard.is_pressed(key):
                action()
                time.sleep(0.2)
                break

if __name__ == "__main__":
    loop_station = LoopStation(bpm=120, beats_per_loop=8)
    kb_thread = threading.Thread(target=keyboard_control, args=(loop_station,))
    kb_thread.daemon = True
    kb_thread.start()
    while loop_station.is_running:
        time.sleep(0.1)