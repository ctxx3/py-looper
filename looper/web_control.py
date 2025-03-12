from flask import Flask, request, render_template
import threading
from waitress import serve  # Added import

def web_control(loop_station):
    app = Flask(__name__)
    
    # Map commands to loop_station methods
    commands = {
         'record1': lambda: loop_station.start_recording(0),
         'record2': lambda: loop_station.start_recording(1),
         'record3': lambda: loop_station.start_recording(2),
         'toggle1': lambda: loop_station.toggle_track(0),
         'toggle2': lambda: loop_station.toggle_track(1),
         'toggle3': lambda: loop_station.toggle_track(2),
         'stop': lambda: loop_station.stop_recording(),
         'bpm_up': lambda: loop_station.change_bpm(loop_station.bpm + 5),
         'bpm_down': lambda: loop_station.change_bpm(max(60, loop_station.bpm - 5)),
         'metronome': lambda: loop_station.toggle_metronome(),
    }
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            cmd = request.form.get('command')
            if cmd in commands:
                commands[cmd]()
        return render_template("index.html")
    
    # Production ready: use Waitress WSGI server
    serve(app, host="0.0.0.0", port=5000)
