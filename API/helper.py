import sounddevice as sd
from flask import session
from flask_socketio import emit
import numpy as np
from  scipy.io import wavfile 
import subprocess



class AudioStream:
	def __init__(self, downsample, samplerate, chunk, channels, session):
		self.downsample = downsample
		self.samplerate = samplerate
		self.chunk = chunk
		self.channels = channels
		self.session = session

	def create_audio_session(self):
		if 'audio' not in session.keys():
			self.session['audio'] = []

	def create_stream(self):
		self.session['stream'] = sd.Stream(samplerate=self.samplerate, channels= self.channels, blocksize=self.chunk)

	def start_stream(self):
		self.session['stream'].start()

	def store_data(self, indata):
		self.session['audio'].extend(indata[::1,0].tolist())

	def downsample_data(self, indata):
		return indata[::self.downsample, 0]

	def read_stream(self):
		return self.session['stream'].read(self.chunk)

	def emit_message(self, data = [0]*1000, time = 0):
		emit('client', {'data': data, 'time': time}, broadcast = False)

	def pause_recorder(self):
		self.session['stream'].abort()
		self.emit_message(time = len(self.session['audio'])/self.samplerate )

	def stop_recorder(self):
		self.emit_message(time = 0)
		self.session['stream'].abort()
		self.session.pop('audio', None)

	def save_wav(self, name):
		self.pause_recorder()
		wavfile.write(name + ".wav", self.samplerate, np.array(self.session['audio']))
		self.emit_message(time = 0)
		self.session['audio'] = []

	def emit_play(self, name, running):
		emit('client_play', {'name': name, 'running': running}, broadcast = False)

	def play_wav(self, name):
		self.emit_play(name, True)
		subprocess.call(["afplay", name + '.wav'])
		self.emit_play(name, False)
