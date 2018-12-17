#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests and send documents
to print, with lp command.

You must set an username and password and send them in a JSON to the server
the printer name will contain all printers (TODO allow to switch between printers)


Usage::
	./server.py [<port>]

POST:

	curl --request POST htt --data '{"username":"username","password":"password",
	"url":"https://example.com/filename.jpeg", "filename":"filename.jpeg", ncopies: 1}' --header "Content-Type: application/json"

"""
import os
import simplejson
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import subprocess

import urllib.request

printers = {
	'default': 'Lexmark_Lexmark_International_Lexmark_MS510dn'
}
username = 'username'
password = 'password'


class S(BaseHTTPRequestHandler):
	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_GET(self):
		logging.info("GET request,\nPath: %s\nHeaders:\n%s\n",
					 str(self.path), str(self.headers))
		self._set_response()
		self.wfile.write("GET request for {}".format(
			self.path).encode('utf-8'))

	def do_POST(self):
		# <--- Gets the size of data
		content_length = int(self.headers['Content-Length'])
		# <--- Gets the data itself
		post_data = self.rfile.read(content_length)

		try:
			jsondata = simplejson.loads(post_data)[0]

			if jsondata["username"] == username and jsondata['password'] == password:
				# set file name, retrieved from post request
				filename = jsondata['filename']

				# download file to print
				urllib.request.urlretrieve(jsondata["url"], 'media/'+filename)


				# configure lp options
				lp_config = {
					"filename": jsondata["filename"],
					"printer_name": printers["default"],
					"ncopies": jsondata["ncopies"]
				}

				# prepare command
				lp_command = "lp media/{filename} -d {printer_name} -n {ncopies}".format_map(lp_config)

				# send file to printer
				subprocess.run(lp_command, shell=True)

				# Delete printed file
				subprocess.run("rm media/" + filename, shell=True)

				logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
							 str(self.path), str(self.headers), post_data)
				self._set_response()
				self.wfile.write("POST request for {}".format(
					self.path).encode('utf-8'))

		except Exception as e:
			print("Exception ocurred", e)

			logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
						 str(self.path), str(self.headers), post_data)

			self._set_response()
			self.wfile.write("POST request for {}".format(
				self.path).encode('utf-8'))
			return


def run(server_class=HTTPServer, handler_class=S, port=8081):
	logging.basicConfig(level=logging.INFO)
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	logging.info('Starting httpd...\n')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	logging.info('Stopping httpd...\n')


# Before starting the server, check if the default port has been changed and if media folder exists
if __name__ == '__main__':
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		if not os.path.exists("media"):
			os.makedirs('media')
		else:
			run()
