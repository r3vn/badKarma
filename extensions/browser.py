import os

class karma_ext():
	def __init__(self):
		#self.url = url
		self.name = "browser"
		self.menu = {"service" : ["http"], "label" : "Open in Browser"}
		self.log = False

	def task(self, config):
		""" open an url with browser"""
		host = config["rhost"]
		port = config["rport"]

		url = host + ":" + port

		if '443' in port:
			url = "https://"+ url
		else:
			url = "http://"+ url
			
		os.system("xdg-open "+url),9999