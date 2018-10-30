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

import sys
import os
import gi

import core.icons as iconslib

try:
	gi.require_version('OsmGpsMap', '1.0')
	gi.require_version('Gtk', '3.0')
	gi.require_version('GtkSource', '3.0') 
	gi.require_version('Vte', '2.91')
	gi.require_version('GtkSource', '3.0') 
	gi.require_version('WebKit2', '4.0') 

except:
	print("[!] Missing dependencies, check setup instructions at readme.md")
	sys.exit()


from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GtkSource
from gi.repository import OsmGpsMap as osmgpsmap
from gi.repository import Vte
from gi.repository import GtkSource
from gi.repository import GLib
from gi.repository import WebKit2

class WebView(WebKit2.WebView):
	def __init__(self, url, proxy=False, *args, **kwargs):
		super(WebView, self).__init__(*args, **kwargs)
		""" WebKit2 Webview widget """

		web_context = WebKit2.WebContext.get_default()
		web_context.set_tls_errors_policy(WebKit2.TLSErrorsPolicy.IGNORE)

		if proxy:
			# proxy False or "http://127.0.0.1:8080"
			web_context.set_network_proxy_settings(WebKit2.NetworkProxyMode.CUSTOM, WebKit2.NetworkProxySettings.new(proxy))
		
		self.set_hexpand(True)
		self.set_vexpand(True)

		self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

		self.address_bar = Gtk.Entry()
		self.go_button = Gtk.Button("go")

		self.address_bar.set_text(url)

		self.toolbar.add(self.address_bar)
		self.toolbar.add(self.go_button)

		if proxy:
			GLib.timeout_add_seconds(2, self._reload)

		self.toolbar.set_hexpand(True)
		self.address_bar.set_hexpand(True)

		self.load_uri(url)
		self.toolbar.show_all()
		self.show_all()

		self.load_uri(url)

		self.connect("load-changed", self._load_changed)
		self.go_button.connect("clicked", self._load_uri)

	def _load_uri(self, widget):
		""" load new uri """

		self.load_uri(self.address_bar.get_text())

	def _load_changed(self, widget, test):
		""" update address bar """

		self.address_bar.set_text(self.get_uri())

	def _reload(self):
		""" workaround to avoid race condition with mitmproxy """

		self.reload()



class SourceView(GtkSource.View):
	def __init__(self, *args, **kwargs):
		super(SourceView, self).__init__(*args, **kwargs)
		""" GtkSource.View widget """
		self.set_show_line_numbers(True)


class Terminal(Vte.Terminal):
	def __init__(self, *args, **kwargs):
		super(Terminal, self).__init__(*args, **kwargs)
		""" Vte terminal widget """

		self.set_scrollback_lines(-1)
		self.set_hexpand(True)

		self.status, self.pid = self.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			["/bin/bash"],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
			)

		self.show()
		self.connect("key-press-event", self._key_press_event)

	def _key_press_event(self, widget, event):
		# Vte terminal key press event,
		# allow Copy/Paste in the terminal

		keyval = event.keyval
		keyval_name = Gdk.keyval_name(keyval)
		state = event.state

		ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
		shift = (state & Gdk.ModifierType.SHIFT_MASK)

		if ctrl and shift and keyval_name == 'C':
			# Ctrl+Shit+C - copy
			self.copy_clipboard_format(Vte.Format.TEXT)

		if ctrl and shift and keyval_name == 'V':
			# Ctrl+Shit+V - paste
			self.paste_clipboard()


class host_informations(Gtk.ScrolledWindow):
	def __init__(self, database, host, *args, **kwargs):
		super(host_informations, self).__init__(*args, **kwargs)
		""" single host information widget """

		builder	 = Gtk.Builder() # glade
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/widgets.glade")

		self.info_viewport  = builder.get_object("host-info-viewport")
		self.info_mac		= builder.get_object("info-mac")
		self.info_os		= builder.get_object("info-os")
		self.info_vendor    = builder.get_object("info-vendor")

		self.info_status	= builder.get_object("info-status")
		self.info_address   = builder.get_object("info-address")
		self.info_hostnames = builder.get_object("info-hostnames")
		self.info_distance  = builder.get_object("info-distance")
		self.info_tcpseq	= builder.get_object("info-tcpseq")
		self.info_uptime	= builder.get_object("info-uptime")
		
		self.info_latitude  = builder.get_object("info-latitude")
		self.info_longitude = builder.get_object("info-longitude")

		self.info_isp          = builder.get_object("info-isp")
		self.info_country_code = builder.get_object("info-country_code")
		self.info_country_name = builder.get_object("info-country_name")
		self.info_organization = builder.get_object("info-organization")

		viewport = Gtk.Viewport()
		viewport.add(self.info_viewport)
		viewport.set_vexpand(True)
		viewport.set_hexpand(True)

		self.add(viewport)
		self.set_property("height-request", 400)
		self.show_all()

		self.database = database
		self.host     = host

		self.refresh(self.database, self.host)

	def refresh(self, database, host):
		# Fill info tab
		self.host = host
		self.database = database

		
		self.info_os.set_text(str(host.os_match))#.split("\n")[0]
		

		hostnamestring = ""
		
		self.info_status.set_text(host.status)

		self.info_hostnames.set_text(host.hostname)

		self.info_address.set_text(host.address)

		self.info_distance.set_text(str(host.distance)+" hops")

		self.info_mac.set_text(host.mac)

		self.info_vendor.set_text(host.vendor)

		self.info_uptime.set_text(str(host.uptime) + " seconds")
		self.info_tcpseq.set_text(host.tcpsequence)
		
		self.info_latitude.set_text(str(host.latitude))
		
		#try:
		self.info_longitude.set_text(str(host.longitude))
		self.info_organization.set_text(str(host.organization))
		self.info_isp.set_text(str(host.isp))
		self.info_country_code.set_text(str(host.country_code))
		self.info_country_name.set_text(str(host.country_name))
		#except: pass

class OSM(osmgpsmap.Map):
	def __init__(self, database, host, *args, **kwargs):
		super(OSM, self).__init__(*args, **kwargs)
		""" single host geolocation map widget """

		self.layer_add(
					osmgpsmap.MapOsd(
						show_dpad=True,
						show_zoom=True,
						show_crosshair=True)
		)


		self.props.has_tooltip = True

		self.host = host
		self.database = database

		self.show()
		self.set_property("height-request", 400)


		self.refresh(self.database, self.host)

	def refresh(self, database, host):
		""" Refresh map """

		lat  = host.latitude
		long = host.longitude

		if lat and long:
			self.gps_add(lat, long, heading=12*360)
		#self.convert_screen_to_geographic(lat, long)



class Historyview(Gtk.TreeView):
	def __init__(self, database, host, *args, **kwargs):
		super(Historyview, self).__init__(*args, **kwargs)
		""" Single host's task history """

		self.database = database
		self.host     = host
	
		self.set_model(Gtk.ListStore(int, str, str, int, str))
		self.history_liststore = self.get_model()

		for i, column_title in enumerate(["id","Started", "Ended", "Pid", "Task"]):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=i)

			self.append_column(column)

		self.show_all()

		self.refresh(self.database, self.host)


	def refresh(self, database, host):
		""" refresh history """
		self.history_liststore.clear()

		self.host     = host
		self.database = database

		self.history  = self.database.get_history(self.host)

		for task in self.history:
			self.history_liststore.append([task.id, task.start_time, task.end_time, task.pid, task.title])



class ServicesTree(Gtk.TreeView):
	def __init__(self, database, service, *args, **kwargs):
		super(ServicesTree, self).__init__(*args, **kwargs)
		""" Single service ports treeview class """

		self.database = database
		self.service = service

		self.set_model(Gtk.ListStore(GdkPixbuf.Pixbuf, int, str, str, str, str, str, int))
		self.port_liststore = self.get_model()

		for i, column_title in enumerate(["#","Port", "State", "Type", "Host", "Banner", "Fingerprint"]):
			if i == 0:

				renderer = Gtk.CellRendererPixbuf()
				column = Gtk.TreeViewColumn(column_title, renderer, pixbuf=0)
			else:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer, text=i)

			self.append_column(column)

		# multi selection
		selection = self.get_selection()
		selection.set_mode(Gtk.SelectionMode.MULTIPLE)

		#self.refresh(self.database, self.host)


	def refresh(self, db, service, scope=True):

		self.database = db
		self.service = service

		self.ports = self.database.get_ports_by_service(self.service, scope=scope)
		self.port_liststore.clear()

		for port in self.ports:
			# fill the list

			ports_list = []

			if port.state == "open" and port.service != "tcpwrapped":
				ports_list.append(iconslib.port_open_icon())
			else:
				ports_list.append(iconslib.port_closed_icon())

			ports_list.append(port.port)
			ports_list.append(port.state)
			ports_list.append(port.protocol)
			ports_list.append(port.host.address)
			ports_list.append(port.banner) #.replace("product: ",""))
			ports_list.append(port.fingerprint)
			ports_list.append(port.id)

			self.port_liststore.append(ports_list)



class PortsTree(Gtk.TreeView):
	def __init__(self, database, host, *args, **kwargs):
		super(PortsTree, self).__init__(*args, **kwargs)
		""" Single host ports treeview class """

		self.set_model(Gtk.ListStore(GdkPixbuf.Pixbuf, int, str, str, str, str, str, int))
		self.port_liststore = self.get_model()
		
		for i, column_title in enumerate(["#","Port", "State", "Type", "Service", "Banner", "Fingerprint"]):
			if i == 0:

				renderer = Gtk.CellRendererPixbuf()
				column = Gtk.TreeViewColumn(column_title, renderer, pixbuf=0)
			else:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer, text=i)

			self.append_column(column)

		self.show_all()

		self.database = database
		self.host     = host

		self.refresh(self.database, self.host)


	def refresh(self, database, host):
		""" Refresh services """
		self.database = database
		self.host     = host

		self.port_liststore.clear()

		ports = self.database.get_ports_by_host(self.host)

		for port in ports:
			# fill the list

			ports_list = []

			if port.state == "open" and port.service != "tcpwrapped":
				ports_list.append(iconslib.port_open_icon())
			else:
				ports_list.append(iconslib.port_closed_icon())
				
			ports_list.append(port.port)
			ports_list.append(port.state)
			ports_list.append(port.protocol)
			ports_list.append(port.service)
			ports_list.append(port.banner) #.replace("product: ",""))
			ports_list.append(port.fingerprint)
			ports_list.append(port.id)

			
			self.port_liststore.append(ports_list)

		self.show_all()


class Notesview(Gtk.ScrolledWindow):
	def __init__(self, database, host, *args, **kwargs):
		super(Notesview, self).__init__(*args, **kwargs)
		""" notes view per host """
		builder = Gtk.Builder()
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/widgets.glade")

		self.notes_view        = builder.get_object("notes-view")
		self.notes_treepl      = builder.get_object("notes-treepl")
		self.add_button        = builder.get_object("add-button")


		self.database = database
		self.host     = host
		
		# notes
		self.notes_view = builder.get_object("notes-view")
		self.notes_liststore = Gtk.ListStore(str, int)

		self.notestree = Gtk.TreeView(model=self.notes_liststore)
		

		for i, column_title in enumerate(["title"]):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			self.notestree.append_column(column)


		self.notes_treepl.add(self.notestree)
		self.notestree.show()
		#self.refresh(self.database)

		self.notestree.connect("row-activated", self.on_row_activated)
		self.add_button.connect("clicked", self.add_note)
		self.notestree.connect("button_press_event", self.mouse_click)

		self.notestree.props.activate_on_single_click = True

		# multi selection
		selection = self.notestree.get_selection()
		selection.set_mode(Gtk.SelectionMode.MULTIPLE)

		viewport = Gtk.Viewport()
		viewport.add(self.notes_view)

		self.set_property("height-request", 400)
		self.add(viewport)
		self.show_all()
		self.refresh(self.database, self.host)


	def refresh(self, database, host):

		self.notes_liststore.clear()

		self.database = database
		self.notes    = self.database.get_notes(self.host.id)

		for nota in self.notes:
			self.notes_liststore.append([nota.title, nota.id])

	def mouse_click(self, tv, event):
		# right click on a note
		try:
			self.rightclickmenu.destroy()
		except: pass

		if event.button == 3:

			# get selected port
			self.rightclickmenu = Gtk.Menu()

			note_selected = []

			(model, pathlist) = tv.get_selection().get_selected_rows()
			for path in pathlist :
				tree_iter = model.get_iter(path)
				
				idz = model.get_value(tree_iter,1)

				note_selected.append(idz)
				
			i1 = Gtk.MenuItem("delete")
			i2 = Gtk.MenuItem("rename")

			i1.connect("activate", self.delete_note, note_selected)
			i2.connect("activate", self.rename_note, note_selected)

				
			self.rightclickmenu.append(i1)
			self.rightclickmenu.append(i2)

			# show all
			self.rightclickmenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
			self.rightclickmenu.show_all()


	def add_note(self, widget):

		""" add a note to the db """

		try:
			self.scrolledwindow.destroy()
		except: pass

		title, id = self.database.add_note(self.host.id, "note "+str(len(self.notes_liststore)), "") # FIXME
		self.notes_liststore.append([title, id])

		self.scrolledwindow = Gtk.ScrolledWindow()
		self.scrolledwindow.set_hexpand(True)
		self.scrolledwindow.set_vexpand(True)

		self.note_box = GtkSource.View()
		textbuffer = self.note_box.get_buffer()
		textbuffer.set_text("")
		self.notestree = Gtk.TreeView(model=self.notes_liststore)
		self.note_box.set_show_line_numbers(True)

		self.scrolledwindow.add(self.note_box)
		self.note_box.show()
		self.scrolledwindow.show()

		self.notes_view.add(self.scrolledwindow)

		self.note_box.connect("move-cursor", self.save_note, id)

		self.id = id

	
	def on_row_activated(self, listbox, cell, listboxrow):

		try:
			self.save_note('','','','',self.id)
			self.scrolledwindow.destroy()
		except: pass

		(model, pathlist) = listbox.get_selection().get_selected_rows()
		for path in pathlist :

			tree_iter = model.get_iter(path)
			id = model.get_value(tree_iter,1)

			nota = self.database.get_note(id)

			self.scrolledwindow = Gtk.ScrolledWindow()
			self.scrolledwindow.set_hexpand(True)
			self.scrolledwindow.set_vexpand(True)

			self.note_box = GtkSource.View()
			textbuffer = self.note_box.get_buffer()
			textbuffer.set_text(nota.text)
			self.notestree = Gtk.TreeView(model=self.notes_liststore)
			self.note_box.set_show_line_numbers(True)

			self.scrolledwindow.add(self.note_box)
			self.note_box.show()
			self.scrolledwindow.show()

			self.notes_view.add(self.scrolledwindow)
			self.note_box.connect("move-cursor", self.save_note, id)

			self.id = id


	def save_note(self, widget, lc, addff, fef, id):

		start_iter = self.note_box.get_buffer().get_start_iter()
		end_iter = self.note_box.get_buffer().get_end_iter()
		text = self.note_box.get_buffer().get_text(start_iter, end_iter, True)  

		self.database.save_note(id, text)

	def rename_note(self, widget, note_selected):
		""" rename a note """

		builder = Gtk.Builder()
		builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../assets/ui/widgets.glade")

		self.rename_note_input = builder.get_object("rename-note-input")
		self.rename_note_win   = builder.get_object("rename-note")
		self.rename_note_save  = builder.get_object("rename-note-save")
		self.rename_note_canc  = builder.get_object("rename-note-canc")


		for idz in note_selected:
			self.rename_note_win.show()
			self.rename_note_win.set_title("rename note")

			self.rename_note_canc.connect('clicked', self._destroy_rename_note)
			self.rename_note_save.connect('clicked', self._save_rename_note, idz)

	def _destroy_rename_note(self, widget):
		""" destroy and get a new rename_note window """
		self.rename_note_win.destroy()


	def _save_rename_note(self, widget, id):
		""" rename note  """
		newname = self.rename_note_input.get_text()
		self.database.rename_note(id,newname)

		self.rename_note_win.destroy()

		self.refresh(self.database, self.host)
			

	def delete_note(self, widget, note_selected):
		# delete a note from the db
		# ask for confirmation with a dialog
		dialog = Gtk.MessageDialog(Gtk.Window(), 0, Gtk.MessageType.WARNING,
			Gtk.ButtonsType.OK_CANCEL, "Delete note?")
		dialog.format_secondary_text(
			"This operation will be irreversible.")
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			dialog.close()

			for note in note_selected:
				self.database.remove_note(note)

			try:
				self.scrolledwindow.destroy()
			except: pass

			self.refresh(self.database, self.host)

		elif response == Gtk.ResponseType.CANCEL:
			dialog.close()
