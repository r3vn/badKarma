#!/usr/bin/env python3
# badKarma - network reconnaissance toolkit
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

class Importers:
	def __init__(self, database):
		""" Session's extensions engine """

		self.modules = {}

		self._indicize_modules(database)

	def _indicize_modules(self, database):
		for dirpath, dirnames, filenames in os.walk(os.path.dirname(os.path.abspath(__file__))+"/../extensions/importers/"):
			for filename in [f for f in filenames if f.endswith(".py")]:
				if filename not in ["__init__.py","__pycache__"]:
					module_name = str(os.path.join(dirpath, filename).replace(".py","").replace(os.path.dirname(os.path.abspath(__file__))+"/../extensions/importers/","") )
					module = importlib.import_module('extensions.importers.'+module_name)
					module = module.karma_ext(database)

					try:
						# check if the module have a menu option
						self.menus[module] = module.menu

					except: pass

					self.modules[module.name] = { 
											"path"   : 'extensions.importers.'+module_name,
											"module" : module
										 }

		return True




class Extensions:
	def __init__(self):
		# initialize extensions

		self.menus = {}
		self.modules  = {}

		self._indicize_modules()



	def get_extra(self, service, all=True):
		""" return menu list of python extension """
		returndict = {}
		for serv in self.menus:

			if "all" in self.menus[serv]["service"]:
				if all:
					returndict[self.menus[serv]["label"]] = serv

			if service in self.menus[serv]["service"]:
				returndict[self.menus[serv]["label"]] = serv


		return returndict



	def get_extra_by_name(self, name):
		""" return an extra object by name """
		
		for serv in self.modules:
			if name == serv:
				return self.modules[serv]["module"]



	def get_new(self, extension_name):
		""" get a new istance of an extension in order to avoid signals override """

		for serv in self.modules:
			if extension_name == serv:
				module = importlib.import_module(self.modules[serv]["path"])

				return module.karma_ext()



	def _indicize_modules(self):
		""" initialize post modules """

		for dirpath, dirnames, filenames in os.walk(os.path.dirname(os.path.abspath(__file__))+"/../extensions/workspace/"):
			for filename in [f for f in filenames if f.endswith(".py")]:
				if filename not in ["__init__.py","__pycache__"]:
					module_name = str(os.path.join(dirpath, filename).replace(".py","").replace(os.path.dirname(os.path.abspath(__file__))+"/../extensions/workspace/","") )
					module = importlib.import_module('extensions.workspace.'+module_name)
					module = module.karma_ext()

					try:
						# check if the module have a menu option
						self.menus[module] = module.menu

					except: pass

					self.modules[module.name] = { 
											"path"   : 'extensions.workspace.'+module_name,
											"module" : module
										 }

		return True
