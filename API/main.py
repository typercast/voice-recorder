from flask import Flask, session
from flask_socketio import SocketIO
import numpy as np
from helper import AudioStream


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on("audio")
def handleAudio(input):
	controller = AudioStream(downsample = 10, samplerate = 44100, chunk = 4096, channels = 1, session = session)
	while input['action'] == 'start':
		if 'audio' not in controller.session.keys():
			controller.create_audio_session()
		if 'stream' not in controller.session.keys() or controller.session['stream'].active == False:
			controller.create_stream()
			controller.start_stream()
		indata, overflowed = controller.read_stream()
		controller.store_data(indata)
		add_data = controller.downsample_data(indata)
		controller.emit_message(data = add_data.tolist(), time = len(controller.session['audio'])/controller.samplerate )
	if input['action'] == 'pause':
		controller.pause_recorder()
	if input['action'] == 'stop':
		controller.stop_recorder()
	if input['action'] == 'save':
		controller.save_wav(input['arg'])
	if input['action'] == 'play':
		controller.play_wav(input['arg'])


if __name__ == "__main__":
	socketio.run(app, host= '0.0.0.0', port = 5001)