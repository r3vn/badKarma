#!/usr/bin/env python3
# badKarma - advanced network reconnaissance toolkit
#
# Copyright (C) 2018 <Giuseppe `r3v` Corti>
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

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import ipaddress
import os

class Targetadd():
	def __init__(self, database):
		# initialization
		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/add.glade")

		self.database = database

		# window
		#self.headerbar = builder.get_object("headerbar")
		self.window        = builder.get_object("window")
		self.cancel_button = builder.get_object("cancel-button")
		self.add_button    = builder.get_object("add-button")
		self.target_input  = builder.get_object("target-input")
		self.hostdiscovery = builder.get_object("hostdiscovery")
		self.errorinfo     = builder.get_object("errorinfo")
		self.nmap_scan_box = builder.get_object("nmap-scan-box")

		nmap_store = Gtk.ListStore(str)
		scan_types = ["nmap_default","nmap_intense_scan","nmap_intense_scan_all_tcp","nmap_intense_scan_no_ping"]

		for scan in scan_types:
			nmap_store.append([scan])

		self.nmap_combo = Gtk.ComboBox.new_with_model_and_entry(nmap_store)
		self.nmap_combo.set_entry_text_column(0)
		self.nmap_combo.set_active(0)
		self.nmap_scan_box.add(self.nmap_combo)
		self.nmap_combo.show()

		self.hostdiscovery.connect("toggled", self._check_nmap)

		self.window.set_title("add target(s)")
		self.window.show()

	
	def _check_nmap(self, caller):

		self.nmap_combo.set_sensitive(self.hostdiscovery.get_active())



	def add_host(self):

		#self.errorinfo.hide()
		targets = self.target_input.get_text()

		try:

			for target in targets.split(" "):
				if "/" in target:
					# get ip from range
					net4 = ipaddress.ip_network(target)

					for x in net4.hosts():
						#print(x)
						self.database.add_host(str(x))


				elif "-" in target:
					# get first ip
					start = target.split("-")[0]
					dot = start.split(".")
					end = target.split("-")[1]

					for t in range(int(dot[3]),int(end)+1):
						ip = dot[0] +"."+ dot[1] +"."+ dot[2] +"."+str(t)

						self.database.add_host(ip)
						#print (ip)
					
				else:
					self.database.add_host(target)

			#self.window.destroy()
			return True

		except:

			self.errorinfo.show()
			return False