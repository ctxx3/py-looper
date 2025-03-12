import time
import threading
import RPi.GPIO as GPIO
from looper.loopstation import LoopStation

def gpio_control(loop_station):
    # Setup GPIO mode
    GPIO.setmode(GPIO.BCM)
    # Define pin mappings
    track_pins = {5: 0, 6: 1, 13: 2}  # mapping pin -> track index
    stop_pin = 19   # clear recordings
    metro_pin = 26  # metronome toggle
    led_record_pin = 20
    led_metro_pin = 21

    # Setup button pins with pull-up resistors
    for pin in track_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(stop_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(metro_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Setup LED pins as output
    GPIO.setup(led_record_pin, GPIO.OUT)
    GPIO.setup(led_metro_pin, GPIO.OUT)
    # Initialize LEDs
    GPIO.output(led_record_pin, False)
    GPIO.output(led_metro_pin, loop_station.metronome_enabled)

    debounce_threshold = 0.2  # seconds
    _last_event_time = {}
    def debounce(channel):
        now = time.time()
        last = _last_event_time.get(channel, 0)
        if now - last < debounce_threshold:
            return False
        _last_event_time[channel] = now
        return True

    # Callback for track buttons (handle both press and release)
    def track_callback(channel):
        if not debounce(channel):
            return
        if GPIO.input(channel) == GPIO.LOW:  # button pressed
            track_index = track_pins[channel]
            loop_station.start_recording(track_index)
            GPIO.output(led_record_pin, True)
        else:  # button released
            loop_station.stop_recording()
            GPIO.output(led_record_pin, False)

    # Callback for stop button to clear recordings
    def stop_callback(channel):
        if not debounce(channel):
            return
        if GPIO.input(channel) == GPIO.LOW:
            loop_station.clear_recordings()
            GPIO.output(led_record_pin, False)

    # Callback for metronome button to toggle metronome
    def metro_callback(channel):
        if not debounce(channel):
            return
        if GPIO.input(channel) == GPIO.LOW:
            loop_station.toggle_metronome()
            GPIO.output(led_metro_pin, loop_station.metronome_enabled)

    # Set event detection for track buttons (both press and release)
    for pin in track_pins:
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=track_callback, bouncetime=200)

    # Set event detection for stop and metronome buttons (on falling edge)
    GPIO.add_event_detect(stop_pin, GPIO.FALLING, callback=stop_callback, bouncetime=200)
    GPIO.add_event_detect(metro_pin, GPIO.FALLING, callback=metro_callback, bouncetime=200)

    print("GPIO controls active. Waiting for button presses...")
    try:
        while loop_station.is_running:
            time.sleep(0.1)
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    loop_station = LoopStation(bpm=120, beats_per_loop=8)
    gpio_thread = threading.Thread(target=gpio_control, args=(loop_station,))
    gpio_thread.daemon = True
    gpio_thread.start()
    try:
        while loop_station.is_running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass