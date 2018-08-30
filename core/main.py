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

import os
import sys
import shutil
import gi
import random
import string

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from core.workspace import *
from core.extensions import Extensions
from core.addtargets import Targetadd
from core.database import DB

import core.file_filters as file_filters

class Handler:
	def __init__(self):
		""" badkarma handler class """

		# initialization
		
		self.tasks	     = {} # task queue
		self.outfiles    = {} # scan import queue
		self.scenes	     = {  # saved Gtk scenes of hostview
								"hosts_view"    : {},
								"services_view" : {},
							} 

		self._selected_opt = {  # user selection dict
								"host"    : "",
								"port"    : "",
								"domain"  : "",
								"service" : ""
							} 

		self.database    = DB()
		self.extensions  = Extensions() # extension engine

		self.on_services_view = False

		# generate main window
		self.main = Main()

		# set db location as window subtitle
		self.main.headerbar.set_subtitle(self.database.db_loc)

		self.main.window.connect("delete-event", self.on_window_delete_event)

		# main menu
		self.main.file_addtarget.connect("clicked", self.add_target)
		self.main.file_quit.connect("clicked", self.on_window_delete_event)
		self.main.file_open.connect("clicked", self.open_file)
		self.main.file_import.connect("clicked", self.import_file)
		self.main.file_save_as.connect("clicked", self.save_file_as)

		self.portlist_empty = True

		# preferences 
		self.main.view_logs.connect("toggled", self._showhide_logs)

		# initialization
		# workspace & hostlist
		self.main.controller_notebook.connect('switch-page', self._controller_switch)

		# generate the logger
		self.logger = Logger(self.database)

		# generate the host list
		self.services_list = Serviceslist(self.database)
		self.host_list     = Hostlist(self.database)

		# generate the services list
		self.main.services_box.add(self.services_list.services_box)
		self.main.hostlist_box.add(self.host_list.host_box)

		# connect host list events
		self.host_list.hosttree.connect("row-activated", self.on_row_activated)
		self.host_list.hosttree.connect("button_press_event", self.host_click)	

		# cennect services slist events
		self.services_list.servicestree.connect("row-activated", self.services_row)	
		self.services_list.servicestree.connect("button_press_event", self.host_click)#self.service_click)

		self.main.main_paned.add2(self.logger.notebook)	
 
		# populate window
		self._sync()

		# show all
		self.main.window.show_all()

	def _sync(self, reset=False):
		""" Sync UI and DB """
		
		# refresh everithing
		self.host_list.refresh(self.database)
		self.services_list.refresh(self.database)

		if reset:
			# called at project switch
			# otherwise will break current running task's log
			self.logger.refresh(self.database)

		# set the db location as headerbar subtitle
		self.main.headerbar.set_subtitle(self.database.db_loc)	

		# refresh the hostviews and servicesview
		for host in self.scenes["hosts_view"]:
			self.scenes["hosts_view"][host].refresh(self.database)

		for service in self.scenes["services_view"]:
			self.scenes["services_view"][service].refresh(self.database)

	def _clear_workspace(self):
		""" remove host_view or services_view notebook """
		try:
			self.main.workspace.remove(self.services_view.notebook)
		except: pass
		try:
			self.main.workspace.remove(self.work.notebook)
		except: pass

		return True

	def _filter_service(self, service):
		""" function to replace service name """
		service = service.replace("soap","http").replace("https","http").replace("ssl","http").replace("http-proxy","http").replace("http-alt","http").replace("ajp13","http").replace("vnc-http","http")
		service = service.replace("microsoft-ds","netbios-ssn")

		return service
		
	def _controller_switch(self, widget, test, newpage):
		""" switch from hostview to services view and vice-versa """
		if newpage == 0:
			try:
				# switch to host view
				self.on_services_view = False
				self.main.workspace.remove(self.services_view.notebook)
				self.main.workspace.add(self.work.notebook)
				self.rightclickmenu.destroy()
			except: pass
		
		elif newpage == 1:
			try:
				# switch to servies view
				self.on_services_view = True
				self.main.workspace.remove(self.work.notebook)
				self.main.workspace.add(self.services_view.notebook)
				self.rightclickmenu.destroy()
			except: pass

	def _showhide_logs(self, widget):
		""" show / hide logs notebook """

		if self.main.view_logs.get_active():
			self.logger.notebook.show()

		else:
			self.logger.notebook.hide()


	def _sensitive_true(self, widget, add):
		# close the add target dialog
		
		if add:
			target = self.add_window.target_input.get_text()
			
			self._selected_opt["host"] = target
			self._selected_opt["service"] = "hostlist"
			self._selected_opt["port"] = 0
			

			if self.add_window.hostdiscovery.get_active():
				# user chose to scan the new host
				# we will add it using the run_ext function
				# using all the accrocco
				active = self.add_window.nmap_combo.get_active()
				model  = self.add_window.nmap_combo.get_model()

				button_workaround = Gtk.Button()
				button_workaround.set_label(model[active][0])

				self.run_extra( button_workaround, self.extensions.get_extra_by_name("shell"), "hostlist")
				self.add_window.window.destroy()
				self.main.window.set_sensitive(True)

			else: 
				# user chose to not scan the host
				# only add it's address to the database
				# and sync the ui
				if self.add_window.add_host():
					self.main.window.set_sensitive(True)
					self._sync()
					self.add_window.window.destroy()

		else:
			self.add_window.window.destroy()
			self.main.window.set_sensitive(True)
		

	def add_target(self, widget):
		""" add one or multiple targets """
		self.main.window.set_sensitive(False)
		self.add_window = Targetadd(self.database)
		self.add_window.cancel_button.connect("clicked", self._sensitive_true, False)
		self.add_window.add_button.connect("clicked", self._sensitive_true, True)
		self.add_window.window.connect("close", self._sensitive_true, False)


	def open_file(self, widget):
		""" open a sqlite project file"""

		dialog = Gtk.FileChooserDialog("Please choose a file", None,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		file_filters.add_filter_database(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_selected = dialog.get_filename()
			try:
				self.database = DB(db_loc=file_selected)
				
			except Exception as e:
				print (e) 
			
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()

		# update the hostlist
		self._clear_workspace()
		self._sync(reset=True)
		

	def save_file_as(self, widget):
		""" save the project's sqlite database """

		dialog = Gtk.FileChooserDialog("Please choose a filename", None,
			Gtk.FileChooserAction.SAVE,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_SAVE, Gtk.ResponseType.OK))


		dialog.set_filename("project")
		file_filters.add_filter_database(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_selected = dialog.get_filename()
			try:
				shutil.copy(self.database.db_loc, file_selected)
			except: pass
			
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()
		

	def import_file(self, widget):
		""" import nmap xml """

		dialog = Gtk.FileChooserDialog("Please choose a file", None,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		file_filters.add_filter_nmap(dialog)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			file_selected = dialog.get_filename()
			try:
				self.database.import_nmap(file_selected)
			except Exception as e:
				print(e) 

			
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()
		self._sync()


	def _delete_host(self, widget):
		""" Delete host from database """

		# ask for confirmation with a dialog
		dialog = Gtk.MessageDialog(self.main.window, 0, Gtk.MessageType.WARNING,
			Gtk.ButtonsType.OK_CANCEL, "Delete host(s)?")
		dialog.format_secondary_text(
			"This operation will be irreversible.")
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			dialog.close()

			(model, pathlist) = self.host_list.hosttree.get_selection().get_selected_rows()
			for path in pathlist :

				tree_iter = model.get_iter(path)
				oldid = model.get_value(tree_iter,4)
				#print(path)
				self.host_list.host_liststore.remove(tree_iter)


				self.database.remove_host(oldid)

			
			self._sync()

		elif response == Gtk.ResponseType.CANCEL:
			dialog.close()

	def services_row(self, listbox, cell, listboxrow):
		""" serviceslist service click event
		    this will generate the scene in the scenes dictionary """

		self._clear_workspace()

		if str(cell) in self.scenes["services_view"]:

			# check if the scene was already loaded
			self.services_view = self.scenes["services_view"][str(cell)]

		else:

			# get selected port
			(model, pathlist) = self.services_list.servicestree.get_selection().get_selected_rows()
			for path in pathlist :

				tree_iter = model.get_iter(path)
				#selected_host = model.get_value(tree_iter,1) 
				selected_service = model.get_value(tree_iter,0) # selected service

				# YO
				self._selected_opt["service"] = selected_service 

			# generate the scene
			self.services_view = Serviceview(selected_service, self.database)
			self.scenes["services_view"][str(cell)] = self.services_view

		# add the scene
		self._selected_opt["service"] = self.services_view.service
		self.main.workspace.add(self.services_view.notebook)

		self.services_view.treeview.connect("button_press_event", self.mouse_click)



	def on_row_activated(self, listbox, cell, listboxrow):
		""" Generate the treeView for the ports """

		self._clear_workspace()

		(model, pathlist) = self.host_list.hosttree.get_selection().get_selected_rows()
		for path in pathlist :

			tree_iter = model.get_iter(path)
			host_id = model.get_value(tree_iter,4) # selected host address

			if str(host_id) in self.scenes["hosts_view"]:
				# check if the scene was already loaded
				self.work = self.scenes["hosts_view"][str(host_id)]

			else: 
				# generate the scene
				db_host = self.database.get_host(host_id)
				self.work = Hostview(db_host, self.database)
				self.scenes["hosts_view"][str(host_id)] = self.work

		# add the scene
		self._selected_opt["host"] = self.work.host.address
		self._selected_opt["domain"] = self.work.host.hostname
		self.main.workspace.add(self.work.notebook)

		self.work.treeview.connect("button_press_event", self.mouse_click)


	def run_multi_extra(self, widget, targets,  ext, service):
		""" take a screenshot on multiple targets """
		for serv in targets:
			try:
				# target is a port
				self._selected_opt["host"] = serv.host.address
				self._selected_opt["port"] = serv.port
			except:
				# target is a host
				self._selected_opt["host"] = serv.address

			self.run_extra(widget, ext, service)


	def host_click(self, tv, event):
		""" right click on a host event """
		
		# grab the right click
		if event.button == 3:

			try:
				self.rightclickmenu.destroy()
			except: pass

			self.rightclickmenu = Gtk.Menu()

			# get selected host
			try:
				targets = []
				if self.on_services_view:
					(model, pathlist) = self.services_list.servicestree.get_selection().get_selected_rows()
				else:
					(model, pathlist) = self.host_list.hosttree.get_selection().get_selected_rows()
				
				if len(pathlist) < 1:
					# right click on nothing
					return False 

				for path in pathlist :
					tree_iter = model.get_iter(path)

					if self.on_services_view:

						service = self._filter_service(model.get_value(tree_iter,0)) # selected service

						for port in self.database.get_ports_by_service(service):
							targets.append(port)

					else:
						#print("provone")
						address = model.get_value(tree_iter,1) # selected host address
						domain = model.get_value(tree_iter,2) # selected host address
						host_id = model.get_value(tree_iter,4)

						targets.append(self.database.get_host(host_id))

						self._selected_opt["host"] = address
						self._selected_opt["domain"] = domain
						self._selected_opt["port"] = 0

				if self.on_services_view:
					extra_name = service

				else:
					i4 = Gtk.MenuItem("Delete")
					i4.show()

					self.rightclickmenu.append(i4)
					i4.connect("activate", self._delete_host)

					extra_name = "hostlist"

				extra = self.extensions.get_extra(extra_name)


				for c_ext in extra:
					tabs = {}

					try:
						for extension in extra[c_ext].submenu(extra_name):

							# remove _ and show spaces
							extension = extension.replace("_"," ")

							if len(extension.split(" ")) > 1:
								if not extension.split(" ")[0] in tabs:

									i3 = Gtk.MenuItem(extension.split(" ")[0])
									i3.show()

									tabs[extension.split(" ")[0]] = []
									tabs[extension.split(" ")[0]].append(Gtk.Menu())
									tabs[extension.split(" ")[0]].append(i3)

									self.rightclickmenu.append(i3)
								
								item = Gtk.MenuItem(extension)
								tabs[extension.split(" ")[0]][0].append(item)

							else:

								item = Gtk.MenuItem(extension)
								item.show()
								self.rightclickmenu.append(item)

							item.connect("activate", self.run_multi_extra, targets, extra[c_ext], extra_name)
					
				
						# show all
						for menu in tabs:
							tabs[menu][0].hide()
							tabs[menu][1].set_submenu(tabs[menu][0])

					except : 
						if self.on_services_view:
							item = Gtk.MenuItem(c_ext)
							item.show()
							self.rightclickmenu.append(item)

							item.connect("activate", self.run_multi_extra, targets, extra[c_ext], service)


				self.rightclickmenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
				self.rightclickmenu.show_all()

				return True

			except Exception as e: print(e)



	def mouse_click(self, tv, event):
		""" right click on a service event """
		
		if event.button == 3:

			try:
				self.rightclick_service_menu.destroy()
				self.rightclickmenu.destroy()
			except: pass

			# create the menu and submenu objects
			self.rightclick_service_menu = Gtk.Menu()
			self.rightclickmenu          = Gtk.Menu()

			targets = []
			generic = []

			# check
			if self.on_services_view:
				#try:
				(model, pathlist) = self.services_view.treeview.get_selection().get_selected_rows()
				
			else:
				(model, pathlist) = self.work.treeview.get_selection().get_selected_rows()

			if len(pathlist) < 1:
				# right click on nothing
				return False 

			# get selected port
			try:
				for path in pathlist :
					tree_iter = model.get_iter(path)

					# set selected port
					selected_port = model.get_value(tree_iter,1) 
					self._selected_opt["port"] = selected_port 


					if self.on_services_view:
						# set selected host if on service view
						self._selected_opt["host"] =  model.get_value(tree_iter,4) 
						targets.append(self.database.get_port(model.get_value(tree_iter,7) ))

					else:
						# set selected service if not on service view
						selected_service = model.get_value(tree_iter,4) # selected service
						targets.append(self.database.get_port(model.get_value(tree_iter,7)))
						self._selected_opt["service"] = selected_service 

			except:
				pass
				
			# fix some multiple names
			self._selected_opt["service"] = self._filter_service(self._selected_opt["service"])

			# get extra extensions
			extra = self.extensions.get_extra(self._selected_opt["service"])

			for extension in extra:
				if extension == "shell":
					# little trick for shell ext
					iE = Gtk.MenuItem(self._selected_opt["service"])
				else:
					iE = Gtk.MenuItem(extension)

				iE.show()
				self.rightclickmenu.append(iE)

				# check if there is a submenu for the current extension
				try:
					tabs = {}
					extension_ext_menu = Gtk.Menu()
					submenu = extra[extension].submenu(self._selected_opt["service"])

					for sub_item in submenu:
						if len(sub_item.split("_")) > 1:
							if not sub_item.split("_")[0] in tabs:
								t = Gtk.MenuItem(sub_item.split("_")[0])
								t.show()
								tabs[sub_item.split("_")[0]] = []
								tabs[sub_item.split("_")[0]].append(Gtk.Menu())
								tabs[sub_item.split("_")[0]].append(t)

					# remove _ and show spaces
					for tab in tabs:
						thetab = Gtk.MenuItem(tabs[tab][1].get_label())
						extension_ext_menu.append(thetab)
						thetab.show()
						thetab.set_submenu(tabs[tab][0])

					for sub_item in submenu:
						sub_item = sub_item.replace("_"," ")

						if len(sub_item.split(" ")) > 1:
							#print(sub_item)
							item = Gtk.MenuItem(sub_item)
								
							tabs[sub_item.split(" ")[0]][0].append(item)

						else:
							# extension in any sub-categories
							item = Gtk.MenuItem(sub_item)
							extension_ext_menu.append(item)
							
						# show and connect the extension
						item.show()
						item.connect('activate', self.run_multi_extra, targets, extra[extension], self._selected_opt["service"])
		
					iE.set_submenu(extension_ext_menu)

				except:
					iE.connect('activate', self.run_multi_extra, targets, extra[extension], self._selected_opt["service"])

				try:
					# try if there is generic for the current extension
					submenu = extra[extension].submenu("generic")

					for sub_item in submenu:
						# remove _ and show spaces
						generic.append(sub_item.replace("_"," "))
				except: pass

			gen_x = self.extensions.get_extra("generic")

			for gen in generic:

				i2 = Gtk.MenuItem(gen)
				i2.show()
				self.rightclickmenu.append(i2)

				i2.connect("activate", self.run_multi_extra, targets, gen_x["shell"], "generic")

			self.rightclickmenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

			return True


	def end_task(self, caller, out, id):
		""" function called when an extension's finish a task """

		self.logger.complete_log(id, out) # complete the logger row of the task
		del self.tasks[id] # delete the task from the running task's dict

		try:
			# check if there is an output file to import
			outfile = self.outfiles[id]

			if os.path.exists(outfile):
				# import the nmap xml and refresh the ui
				self.database.import_nmap(outfile)
				self._sync()

		except: pass

		

	def run_extra(self, widget, ext, service): # def run_extra_thread(self, widget, ext, service):
		""" run a python extension """

		# get target strings
		port_string = str(self._selected_opt["port"])
		host_string = self._selected_opt["host"]

		# set the output_file location string
		output_file = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) 
		output_file = "/tmp/badkarma-" + output_file + ".xml"

		# config for the extension
		ext_conf = { 
				"autoexec"      : self.main.auto_exec.get_active(),
				"proxychains"   : self.main.use_proxychains.get_active(),
				"rhost"         : host_string,
				"rport"         : port_string,
				"menu-sel"      : widget.get_label(), 
				"service"       : service, 
				"domain"        : self._selected_opt["domain"],
				"outfile"       : output_file,
				"path_config"   : os.path.dirname(os.path.abspath(__file__)) + "/../conf/",
				"path_script"   : os.path.dirname(os.path.abspath(__file__)) + "/../scripts/",
				"path_wordlist" : os.path.dirname(os.path.abspath(__file__)) + "/../wordlists/"

				}

		ext = self.extensions.get_new(ext.name) # new instance fix for termination signal
		out, pid = ext.task( ext_conf ) # get output and task pid
		
		# define title for logger and notebook's tabs
		if ext.name == "shell":
			task_name = widget.get_label()
		else:
			task_name = ext.name

		task_title = task_name+" "+host_string

		if ext.log:
			
			if port_string != "0":
				task_title += ":"+port_string

			id = self.logger.add_log(pid , task_title, ext.name)
			ext.connect('end_task', self.end_task, id)
			self.outfiles[id] = output_file 

		try:
			views = ext.read(out)
			views.show()
			try:
				self.tasks[id] = { "views" : views, "ext" : ext }
			except: pass
			
			# box label + close button for extension
			box_label = Gtk.Box(spacing=6)
			box_label.add( Gtk.Label(task_title) )
			close_image = Gtk.Image.new_from_icon_name( "gtk-delete", Gtk.IconSize.MENU )
			close_button = Gtk.Button()
			close_button.set_relief(Gtk.ReliefStyle.NONE)
			close_button.add(close_image)
			box_label.add( close_button )

			# close task window option
			close_button.connect("clicked", self.close_task_tab, views)

			if self.on_services_view:
				self.services_view.notebook.append_page(views,box_label)
				self.services_view.notebook.set_current_page(-1)
			else:
				self.work.notebook.append_page(views,box_label)
				self.work.notebook.set_current_page(-1)

			box_label.show_all()

		except: pass

		return True


	def close_task_tab(self, btn, widget):
		""" event triggered at close button's click """

		if self.on_services_view:
			current_tab = self.services_view.notebook.page_num(widget)
			self.services_view.notebook.remove_page(current_tab)
		else:
			current_tab = self.work.notebook.page_num(widget)
			self.work.notebook.remove_page(current_tab)

		
	def on_window_delete_event(self, *args):
		# quit

		Gtk.main_quit(*args)
		sys.exit()