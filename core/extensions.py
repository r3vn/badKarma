#!/usr/bin/env python3
# badKarma - network reconnaissance toolkit
# ( https://badkarma.xfiltrated.com )
#
# Copyright (C) 2018 <Giuseppe `r3vn` Corti>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import importlib
import random
import string
import configparser
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GObject

from core.database import DB

class karmaEngine(GObject.GObject):
	
	__gsignals__ = {
		"end_task" : (GObject.SIGNAL_RUN_FIRST, None, (int,str,))
	}

	def __init__(self, session_file='/tmp/session.karma'):
		""" Extensions engine """
		GObject.GObject.__init__(self)

		self.database = DB(session_file)
		self.extensions = {
							"workspace": {},
							"importers": {}
		}

		self.cwd = os.path.dirname(os.path.abspath(__file__))
		self.outfiles = {}
		self.tasks = []


		self.id = 1

		for dirpath, dirnames, filenames in os.walk(self.cwd+"/../extensions/"):
			for filename in [f for f in filenames if f.endswith(".py")]:
				if filename in ["__init__.py","__pycache__"]:
					continue # exclude python stuff

				#print(dirpath+"/"+filename)
				module_name = str(os.path.join(dirpath, filename).replace(".py","").replace(self.cwd+"/../extensions/","") ).replace('/','.')
				module      = importlib.import_module('extensions.'+module_name)
					
				module      = module.karma_ext()

				
				if hasattr( module, 'task' ) and callable(module.task): 
					# module have tasks
					self.extensions["workspace"][module.name] = { 
													"path"   : 'extensions.'+module_name,
													"module" : module
					}				
				

				if hasattr( module, 'parse' ) and callable(module.parse):
					# module have importer
					self.extensions["importers"][module.name] = { 
													"path"   : 'extensions.'+module_name,
													"module" : module
					}				



	def get_menu(self, service, all=True):
		""" return menu list of  extension """
		returndict = {}
		for extension in self.extensions["workspace"]:

			for serv in self.extensions["workspace"][extension]["module"].menu["service"]:

				if "all" in serv:
					if all:
						returndict[self.extensions["workspace"][extension]["module"].menu["label"]] = self.extensions["workspace"][extension]["module"]

				if service in self.extensions["workspace"][extension]["module"].menu["service"]:
					returndict[self.extensions["workspace"][extension]["module"].menu["label"]] = self.extensions["workspace"][extension]["module"]

		return returndict



	def get_extension(self, name):
		""" return an extra object by name """
		
		for serv in self.extensions["workspace"]:
			if name == serv:
				module = importlib.import_module(self.extensions["workspace"][serv]["path"])

				return module.karma_ext()



	def get_log(self, extension_name, output):

		return self.extensions['workspace'][extension_name]["module"].get_log(output)

	def import_file(self, path):
		""" import a scan output file """
		if os.path.exists(path):
			with open(path) as myfile:
				head = "".join(myfile.readlines()[0:5]).replace('\n','')

				for extension in self.extensions["importers"]:
					if self.extensions["importers"][extension]["module"].match(head):
						try:
							self.extensions["importers"][extension]["module"].parse(path, self.database)
							#print("parsed")
						except Exception as E:
							print("karmaExt exception:")
							print(self.extensions["importers"][extension]["module"].name)
							print("---")
							print(E)


	def end_task(self, caller, out, id):
		""" function called when an extension's finish a task """

		outfile = self.outfiles[id]
		self.import_file(outfile)

		if os.path.exists(outfile):
			os.remove(outfile)
		
		self.emit('end_task', id, out)


	def start_task(self, extension_name, task, rhost, rport=0, proto="tcp", service_str="hostlist", karmaconf={"autoexec":True, "proxychains":False}):
		""" run a python extension """

		# get extension
		ext = self.get_extension(extension_name)

		# set the output_file location string
		output_file = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) 
		output_file = "/tmp/badkarma-" + output_file + ".xml"

		# check if we have data
		host = self.database.get_host_by_name(rhost)
		if host:

			try:
				domain = host.hostname.split()[0]
			except:
				domain = host.hostname

			service_obj = self.database.get_host_service(host.id, rport, proto)

			try:
				if service_str == "http":
					# Vhost test
					if domain:
						rhost = domain # vhosts test
			except: pass
	
			if service_obj:
				banner = service_obj.banner

			else:
				banner = ""

			service = service_str

		else: 
			# no informations in session
			service = service_str
			domain = ""
			banner = ""

		# config for the extension
		ext_conf = { 
				"autoexec"      : karmaconf["autoexec"],
				"proxychains"   : karmaconf["proxychains"],
				"rhost"         : rhost,
				"rport"         : str(rport),
				"menu-sel"      : task, 
				"service"       : service, 
				"domain"        : domain,
				"banner"        : banner,
				"proto"         : proto,
				"outfile"       : output_file,
				"path_config"   : os.path.abspath(str(os.path.dirname(os.path.realpath(__file__)) ) + "/../conf"),
				"path_script"   : os.path.abspath(str(os.path.dirname(os.path.realpath(__file__)) ) + "/../scripts"),
				"path_wordlist" : os.path.abspath(str(os.path.dirname(os.path.realpath(__file__)) ) + "/../wordlists")

				}

		out, pid = ext.task( ext_conf ) # get output and task pid
		
		task_title = task

		try:
			task_target = host.address
		except: 
			task_target = host

		if ext.log:
			
			if rport != 0:
				task_target += ":"+str(rport)

			ext.connect('end_task', self.end_task, self.id)
			self.outfiles[self.id] = output_file 

			self.id += 1

		return ext.read(out), pid, self.id-1


class base_ext(GObject.GObject):
	""" 
	base extension template, includes: end_task signal, 
	config and assets engine.
	"""
	
	__gsignals__ = {
		"end_task" : (GObject.SIGNAL_RUN_FIRST, None, (str,))
	}

	def __init__(self):
		
		GObject.GObject.__init__(self)


	def conf(self):
		""" get an extension's config file """
		try:

			config_file = configparser.ConfigParser()
			config_file.read( "%s/../conf/%s.conf" % (os.path.dirname(os.path.abspath(__file__)), self.name) )

			return config_file

		except:

			return False

	def gui(self):
		""" get an extension's builder object """
		try:

			builder	 = Gtk.Builder() # glade
			builder.add_from_file( "%s/../assets/ui/%s.glade" % (os.path.dirname(os.path.abspath(__file__)), self.name) )

			return builder

		except:

			return False