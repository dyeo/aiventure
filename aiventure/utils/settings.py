import json
from os import path

class Settings(object):
	"""
	The settings for this application.
	"""

	def __init__(self, filename, defaults):
		self.filename = filename
		if not path.exists(self.filename):
			self.data = defaults
			self.save()
		else:
			self.load()

	def __getitem__(self, key):
		return self.data[key]

	def __setitem__(self, key, value):
		self.data[key] = value

	def load(self):
		with open(self.filename, 'r') as json_file:
			self.data = json.load(json_file)

	def save(self):
		with open(self.filename, 'w') as json_file:
			json.dump(self.data, json_file, indent=4)

