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
import gi
import configparser

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk

from core import widgets
from core.extensions import base_ext

class karma_ext(base_ext):

	name = "metasploit"
	log = True
	menu = { "service" : ["all"], "label" : "metasploit" }

	def _service_filter(self, service):

		return service.replace('netbios-ssn','samba').replace('postgresql','postgres').replace('domain','dns').replace('rpcbind','rpc')

	def _indicize(self):
		""" indicize metasploit modules """
		final = { 
			"auxiliary": {},
			"exploits": {}
		}

		config_file = self.conf()

		if os.path.exists(config_file["default"]["metasploit_path"]): # Fix #13

			for directory in final:

				auxiliary = os.listdir( "%s/modules/%s/" % (config_file["default"]["metasploit_path"],directory) )

				for aux in auxiliary:
					try: 
						services = os.listdir( "%s/modules/%s/%s/" % (config_file["default"]["metasploit_path"], directory, aux) ) 
					except: next
						
					final[directory][aux] = {}
			
					for service in services:
						try: 
							msfmodules = os.listdir( "%s/modules/%s/%s/%s/" % (config_file["default"]["metasploit_path"], directory, aux, service) )
					
							final[directory][aux][service] = []

							for mod in msfmodules:
								final[directory][aux][service].append(mod)

						except: pass

		return final


	def submenu(self, service):
		if service == "generic" or service == "hostlist":
			return False

		menu = {}
		msfmodules = self._indicize()

		for cat in msfmodules:
			for typ in msfmodules[cat]:
				service = self._service_filter(service)
				if service in msfmodules[cat][typ]:
					for mod in msfmodules[cat][typ][service]:
						menu[ cat+"/"+typ+"/"+mod.replace('.rb','').replace('_',' ') ] = ''

		return menu

	def task(self, config):
		""" prepare the shell """
		ext          = config["menu-sel"].replace(" ","_")
		serv         = self._service_filter(config["service"])
		proxychains  = config["proxychains"]
		auto_exec    = config["autoexec"]
		rhost        = config["rhost"]
		rport        = config["rport"]
		banner       = config["banner"]
		output_file  = config["outfile"]
		path_config  = config["path_config"]
		path_script  = config["path_script"]

		# fix ext
		ext_i = ext.split("/")[:-1]
		ext_i.append(serv)
		ext_i.append(ext.split("/")[-1])

		ext = '/'.join(ext_i)

		scroller    = Gtk.ScrolledWindow()

		terminal	= widgets.Terminal() #shell="/usr/bin/msfconsole")

		scroller.add(terminal)
		scroller.show()

		status = terminal.status
		pid = terminal.pid

		startmsf =""
		if proxychains:
			startmsf = "proxychains "
		startmsf+="msfconsole -q\n"

		terminal.feed_child( startmsf.encode() ) 
		terminal.feed_child( ("use %s\n" % (ext)).encode() ) 
		terminal.feed_child( ("set RHOSTS %s\n" % (rhost)).encode() )
		terminal.feed_child( ("set RHOST %s\n" % (rhost)).encode() )
		terminal.feed_child( ("set RPORT %s\n" %(rport)).encode() )

		if auto_exec:
			terminal.feed_child( ("run\n").encode() )
			terminal.feed_child( ("exit\n").encode() )	
			terminal.feed_child( ("exit\n").encode() )	

		terminal.connect("child_exited", self.task_terminated)

		return scroller, pid


	def task_terminated(self, widget, two):

		self.emit('end_task', str(widget.get_text_range(0,0,widget.get_cursor_position()[1] + widget.get_row_count(),10)[0]))


	def read(self, output):
		""" default shell reader """
		return output

	def get_log(self, output):
		""" default shell logger extension"""

		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_hexpand(True)
		scrolledwindow.set_vexpand(True)

		textview = widgets.SourceView()
		textbuffer = textview.get_buffer()
		textbuffer.set_text(output)

		textview.set_editable(False)

		scrolledwindow.add(textview)
		textview.show()

		return scrolledwindow
