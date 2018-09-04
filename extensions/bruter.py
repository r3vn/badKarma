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
import signal
import configparser

gi.require_version('GtkSource', '3.0') 
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkSource
from gi.repository import GLib
from gi.repository import Vte
from gi.repository import GObject

class karma_ext(GObject.GObject):
	
	__gsignals__ = {
		"end_task" : (GObject.SIGNAL_RUN_FIRST, None, (str,))
	}

	def __init__(self):
		""" bruter integrated extension """
		GObject.GObject.__init__(self)

		self.name = "bruter"
		self.log = True
		self.menu = { "service" : ["all"], "label" : "Send to Bruter" }

	def get_log(self, output):
		""" bruter read function, (parser could be implemented?)"""

		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_hexpand(True)
		scrolledwindow.set_vexpand(True)

		textview = GtkSource.View()
		textbuffer = textview.get_buffer()
		textbuffer.set_text(output)

		textview.set_show_line_numbers(True)
		textview.set_editable(False)

		scrolledwindow.add(textview)
		textview.show()

		return scrolledwindow

	def task(self, config):

		serv          = config["service"]
		self.proxy    = config["proxychains"]
		auto_exec     = config["autoexec"]
		rhost         = config["rhost"]
		rport         = config["rport"]
		output_file   = config["outfile"]
		path_config   = config["path_config"]
		path_wordlist = config["path_wordlist"]
		path_script   = config["path_script"]

		config_file = configparser.ConfigParser()
		config_file.read(config["path_config"] + "/bruter.conf")


		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/bruter.glade")

		self.running = False
		self.bruter_box = builder.get_object("bruter-box")

		self.bruter_host		   = builder.get_object("bruter-host")
		self.bruter_port		   = builder.get_object("bruter-port")
		self.bruter_threads		   = builder.get_object("bruter-threads")
		self.bruter_terminal_loc   = builder.get_object("bruter-terminal-loc")
		self.bruter_start		   = builder.get_object("bruter-start")
		self.bruter_service		   = builder.get_object("bruter-service")
		self.bruter_user_box	   = builder.get_object("bruter-user-box")
		self.bruter_user_checkbox  = builder.get_object("bruter-user-wordlsit-checkbox")
		self.bruter_user_wl_path   = builder.get_object("bruter-user-wordlist")
		self.bruter_pass_wl_path   = builder.get_object("bruter-pass-wordlist")
		self.bruter_user_wl_open   = builder.get_object("bruter-user-wordlist-open")
		self.bruter_pass_wl_open   = builder.get_object("bruter-pass-wordlist-open")

		self.bruter_reversed	   = builder.get_object("reversed")
		self.bruter_login_as_pass  = builder.get_object("login-as-pass")
		self.bruter_blank_pass     = builder.get_object("blank-pass")
		self.bruter_use_ssl        = builder.get_object("use-ssl")
		self.bruter_exit_on_first  = builder.get_object("exit-on-first-good")

		self.bruter_terminal = Vte.Terminal()

		self.bruter_terminal_loc.add(self.bruter_terminal)

		self.bruter_user_checkbox_enabled = False
		self.bruter_user_box.set_sensitive(True)
		self.bruter_user_wl_path.set_sensitive(False)
		self.bruter_user_wl_open.set_sensitive(False)

		self.bruter_user_wl_open.connect("clicked", self.bruter_open_user_file)
		self.bruter_pass_wl_open.connect("clicked", self.bruter_open_pass_file)
		self.bruter_start.connect("clicked", self._bruter_start)

		# filil the service combo-box
		name_store = Gtk.ListStore(str)
		hydra_services = ["afp", "asterisk", "cisco-enable", "cisco", "cvs", "firebird", "ftp",
				"http-proxy-urlenum", "http-proxy", "http-get","http-head","https-get", "https-head", "icq", "imap",
				"irc", "ldap", "mssql",	"mysql", "ncp",	"nntp",	"oracle-listener", "oracle-sid",
				"oracle", "pcanywhere",	"pcnfs", "pop3", "postgres", "rdp",	"redis", "rexec",
				"rlogin", "rpcap", "rsh", "rtsp", "s7-300", "sapr3", "sip", "smb","smtp-enum",
				"smtp", "snmp",	"socks5", "ssh", "ssh-key",	"svn", "teamspeak",	"telnet",
				"time", "vmauthd", "vnc", "xmpp"]

		for service in hydra_services:
			name_store.append([service])

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

		self.bruter_service_combo = Gtk.ComboBox.new_with_model_and_entry(name_store)
		self.bruter_user_checkbox.connect("toggled", self._bruter_check_user)
		self.bruter_service_combo.set_entry_text_column(0)
		vbox.pack_start(self.bruter_service_combo, False, False, 0)

		self.bruter_service.add(vbox)

		# bruter wordlists
		default_user_wordlist = config_file["default"]["user_wordlist"].replace("$wordlists", path_wordlist)
		defautl_pass_wordlist = config_file["default"]["pass_wordlist"].replace("$wordlists", path_wordlist)

		self.bruter_user_wl_path.set_text(default_user_wordlist)
		self.bruter_pass_wl_path.set_text(defautl_pass_wordlist)

		self.bruter_box.show_all()

		status, self.pid = self.bruter_terminal.spawn_sync(
				Vte.PtyFlags.DEFAULT,
				os.environ['HOME'],
				["/bin/bash"],
				[],
				GLib.SpawnFlags.DO_NOT_REAP_CHILD,
				None,
				None,

			)
		
		self.bruter_terminal.set_scrollback_lines(-1)
		self.bruter_terminal.connect("key-press-event",self._key_press_event)
		self.bruter_terminal.connect("child_exited", self.task_terminated)
		self.bruter_terminal.hide()

		self.bruter_host.set_text(rhost)
		self.bruter_port.set_text(rport)

		# set default values
		self.bruter_blank_pass.set_active(config_file.getboolean("default", "blank_password"))
		self.bruter_login_as_pass.set_active(config_file.getboolean("default", "try_login_as_password"))
		self.bruter_use_ssl.set_active(config_file.getboolean("default", "use_ssl"))
		self.bruter_exit_on_first.set_active(config_file.getboolean("default", "exit_on_first_good"))
		self.bruter_user_checkbox.set_active(config_file.getboolean("default", "brute_force_user"))

		self.bruter_threads.set_text(config_file["default"]["threads"])
		self.bruter_user_box.set_text(config_file["default"]["user"])

		service_model = self.bruter_service_combo.get_model()

		iter1 = 0
		for ser in service_model:
			if ser[0] == config["service"]: 
				break

			iter1 += 1
		
		self.bruter_service_combo.set_active(iter1)

		if config["autoexec"]:
			self._bruter_start('test')

		return self.bruter_box, self.pid

	def read(self, output):
		return output

	def task_terminated(self, widget, two):
		self.bruter_box.set_sensitive(False)

		self.emit('end_task', str(widget.get_text_range(0,0,widget.get_cursor_position()[1] + widget.get_row_count(),10)[0]))

	def _key_press_event(self, widget, event):
		# Vte terminal key press event,
		# allow Copy/Paste in the terminal

		terminal = widget

		keyval = event.keyval
		keyval_name = Gdk.keyval_name(keyval)
		state = event.state

		ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
		shift = (state & Gdk.ModifierType.SHIFT_MASK)

		if ctrl and shift and keyval_name == 'C':
			# Ctrl+Shit+C - copy
			terminal.copy_clipboard_format(Vte.Format.TEXT)

		if ctrl and shift and keyval_name == 'V':
			# Ctrl+Shit+V - paste
			terminal.paste_clipboard()

	def _bruter_start(self, widget):
		# start the bruite force process
		if self.bruter_start.get_label() == "start":

			cmd = "hydra -t "+self.bruter_threads.get_text()+" " #-l root -P /usr/share/wordlists/dnsmap.txt 127.0.0.1 ssh"]


			if self.bruter_reversed.get_active() or self.bruter_blank_pass.get_active()  or self.bruter_login_as_pass.get_active() :
				cmd += "-e "

				if self.bruter_reversed.get_active():
					cmd += "r"

				if self.bruter_blank_pass.get_active():
					cmd += "n"

				if self.bruter_login_as_pass.get_active():
					cmd += "s"

				cmd += " "

			if self.bruter_use_ssl.get_active():
				cmd += "-S "

			if self.bruter_exit_on_first.get_active():
				cmd += "-F "

			if self.bruter_user_checkbox.get_active():
				# brute force usernames
				cmd += "-L " + self.bruter_user_wl_path.get_text()
			else:
				# use provided user
				cmd += "-l " + self.bruter_user_box.get_text()

			# pass wordlist path
			cmd += " -P " + self.bruter_pass_wl_path.get_text()

			# pass port
			cmd += " -s " + self.bruter_port.get_text()

			# pass host
			cmd += " " + self.bruter_host.get_text()

			# pass service
			active = self.bruter_service_combo.get_active()
			model  = self.bruter_service_combo.get_model()
			cmd   += " " + model[active][0] + "; exit;\n"

			# add proxychain
			if self.proxy:
				cmd = "proxychains "+cmd

			# add the tasks

			self.bruter_start.set_label("stop")
			self.bruter_terminal.show()
			#self.bruter_terminal.feed_child(cmd, len(cmd))	
			self.bruter_terminal.feed_child(cmd.encode())
			#self.bruter_terminal.connect("child_exited", self.task_terminated)
			

		else:
			os.killpg(os.getpgid(self.pid), signal.SIGKILL)
			#self.bruter_terminal.feed_child(signal.SIGINT, 2)	
			#self.bruter_start.set_label("start")
			self.bruter_start.set_sensitive(False)

	def _bruter_check_user(self, widget):

		if not self.bruter_user_checkbox.get_active():
			self.bruter_user_wl_path.set_sensitive(False)
			self.bruter_user_wl_open.set_sensitive(False)
			self.bruter_user_box.set_sensitive(True)
		else:
			self.bruter_user_wl_open.set_sensitive(True)
			self.bruter_user_wl_path.set_sensitive(True)
			self.bruter_user_box.set_sensitive(False)


	def bruter_open_user_file(self ,widget):
		dialog = Gtk.FileChooserDialog("Please choose a file", None,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters_wordlist(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_selected = dialog.get_filename()
			self.bruter_user_wl_path.set_text(file_selected)
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()

	def bruter_open_pass_file(self ,widget):
		dialog = Gtk.FileChooserDialog("Please choose a file", None,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters_wordlist(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_selected = dialog.get_filename()
			self.bruter_pass_wl_path.set_text(file_selected)
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()

	def add_filters_wordlist(self, dialog):
		filter_text = Gtk.FileFilter()
		filter_text.set_name("txt wordlsit")
		filter_text.add_mime_type("text/plain")
		dialog.add_filter(filter_text)

		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
