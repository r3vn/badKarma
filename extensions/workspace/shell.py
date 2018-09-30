#!/usr/bin/env python3
# badKarma - advanced network reconnaissance toolkit
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
from gi.repository import GObject

from core import widgets

class karma_ext(GObject.GObject):

	__gsignals__ = {
		"end_task" : (GObject.SIGNAL_RUN_FIRST, None, (str,))
	}

	def __init__(self):
		""" shell extension """
		GObject.GObject.__init__(self)

		self.config = configparser.ConfigParser()
		self.config.read(os.path.dirname(os.path.abspath(__file__)) + "/../../conf/shell.conf")

		self.name = "shell"
		self.log = True
		self.menu = { "service" : ["all"], "label" : "shell" }

	def submenu(self, service):
		return self.config[service]


	def task(self, config):
		""" prepare the shell """
		ext          = config["menu-sel"].replace(" ","_")
		serv         = config["service"]
		proxychains  = config["proxychains"]
		auto_exec    = config["autoexec"]
		rhost        = config["rhost"]
		rport        = config["rport"]
		output_file  = config["outfile"]
		path_config  = config["path_config"]
		path_script  = config["path_script"]

		cmd = self.config[serv][ext]
		cmd = cmd.replace("$rhost", rhost).replace("$rport", str(rport))
		cmd = cmd.replace('$domain', config["domain"])
		cmd = cmd.replace('$wordlists', config["path_wordlist"])
		cmd = cmd.replace('$scripts', config["path_script"])

		if "$outfile" in cmd:
			# set the output_file location string
			cmd          = cmd.replace("$outfile", output_file)

		if proxychains:
			cmd = "proxychains "+cmd

		cmd += "; exit;"

		if auto_exec:
			cmd+="\n"

		scroller    = Gtk.ScrolledWindow()
		terminal	= widgets.Terminal()

		scroller.add(terminal)
		scroller.show()

		status = terminal.status
		pid = terminal.pid

		terminal.feed_child(cmd.encode())
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
