import time
import threading
from looper.loopstation import LoopStation
from gpiozero import Button, LED

def gpio_control(loop_station):
    # Create a dummy device with no-op methods for LEDs
    class DummyDevice:
        def on(self): pass
        def off(self): pass
    
    def safe_button(pin):
        try:
            return Button(pin)
        except Exception as e:
            print(f"Error initializing Button({pin}):", e)
            return None

    def safe_led(pin):
        try:
            return LED(pin)
        except Exception as e:
            print(f"Error initializing LED({pin}):", e)
            return DummyDevice()

    # Initialize devices individually
    btn_track1 = safe_button(5)
    btn_track2 = safe_button(6)
    btn_track3 = safe_button(13)
    btn_stop   = safe_button(19)  # Now used to clear recordings
    btn_metro  = safe_button(21)
    led_record = safe_led(20)
    led_metro  = safe_led(21)
    
    led_record.off()
    if loop_station.metronome_enabled:
        led_metro.on()
    else:
        led_metro.off()
    
    def on_track_pressed(track_index):
        loop_station.start_recording(track_index)
        led_record.on()
        
    def on_track_released():
        loop_station.stop_recording()
        led_record.off()

    def on_clear_recordings():
        loop_station.clear_recordings()  # Assumes clear_recordings exists in LoopStation
        led_record.off()
    
    def on_toggle_metronome():
        loop_station.toggle_metronome()
        if loop_station.metronome_enabled:
            led_metro.on()
        else:
            led_metro.off()
    
    # Assign events only if buttons were initialized successfully
    if btn_track1:
        btn_track1.when_pressed = lambda: on_track_pressed(0)
        btn_track1.when_released = on_track_released
    if btn_track2:
        btn_track2.when_pressed = lambda: on_track_pressed(1)
        btn_track2.when_released = on_track_released
    if btn_track3:
        btn_track3.when_pressed = lambda: on_track_pressed(2)
        btn_track3.when_released = on_track_released
    if btn_stop:
        btn_stop.when_pressed = on_clear_recordings
    if btn_metro:
        btn_metro.when_pressed = on_toggle_metronome
    
    print("GPIO controls active. Waiting for button presses...")
    while loop_station.is_running:
        time.sleep(0.1)

if __name__ == "__main__":
    loop_station = LoopStation(bpm=120, beats_per_loop=8)
    gpio_thread = threading.Thread(target=gpio_control, args=(loop_station,))
    gpio_thread.daemon = True
    gpio_thread.start()
    while loop_station.is_running:
        time.sleep(0.1)