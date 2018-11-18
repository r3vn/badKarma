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
import sys
import shutil
import gi
import random
import json
import string

try:
	gi.require_version('Gtk', '3.0')
except:
	print("[!] Gtk 3 Missing?")

from gi.repository import Gtk

from core.workspace import *
from core.extensions import karmaEngine
from core.addtargets import Targetadd

import core.file_filters as file_filters

class Handler():
	def __init__(self, engine):
		""" badkarma handler class """

		# initialization
		
		self.scenes	     = {  # saved Gtk scenes of hostview
								"hosts_view"    : {},
								"services_view" : {},
							} 

		self._selected_opt = {  # user selection dict
								"host"    : "",
								"port"    : "",
								"domain"  : "",
								"service" : "",
								"banner"  : "",
							} 

		self.engine      = engine
		self.ext_session = self.engine.extensions["importers"]

		self.on_services_view = False

		# generate main window
		self.main = Main()

		# set db location as window subtitle
		self.main.headerbar.set_subtitle(self.engine.database.db_loc)

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
		self.main.out_of_scope.connect("toggled", self._showhide_scope)

		# initialization
		# workspace & hostlist
		self.main.controller_notebook.connect('switch-page', self._controller_switch)

		# generate the logger
		self.logger = Logger(self.engine.database)

		# generate the host list
		self.services_list = Serviceslist(self.engine.database)
		self.host_list     = Hostlist(self.engine.database)

		# generate the services list
		self.main.services_box.add(self.services_list.services_box)
		self.main.hostlist_box.add(self.host_list.host_box)

		# connect host list events
		self.host_list.hosttree.connect("row-activated", self.on_row_activated)
		self.host_list.hosttree.connect("button_press_event", self.host_click)	

		# cennect services slist events
		self.services_list.servicestree.connect("row-activated", self.services_row)	
		self.services_list.servicestree.connect("button_press_event", self.mouse_click, True)#self.service_click)


		# add welcome messages
		self.main.workspace.add(self.main.welcome_note)
		#self.main.workspace.add(self.services_view.welcome_note)

		# add logger
		self.main.main_paned.add2(self.logger.notebook)	

		# connect extension signal
		self.engine.connect('end_task', self.end_task)

 
		# populate window
		self._sync()

		# show all
		self.main.window.show_all()

	def _sync(self, reset=False, history=False):
		""" Sync UI and DB """

		# Check history refresh
		if history:
			# this sync only the hosts history in the hostviews loaded
			# this avoid to refresh everything and lose the hostlist/servicelist selection
			# then return True

			for host in self.scenes["hosts_view"]:
				self.scenes["hosts_view"][host].refresh(self.engine.database, history=True)

			return True 
		
		# refresh everithing
		self.host_list.refresh(self.engine.database)
		self.services_list.refresh(self.engine.database)

		if reset:
			# called at project switch
			# otherwise will break current running task's log
			self.logger.refresh(self.engine.database)

			# add the welcome message
			self.main.workspace.add(self.main.welcome_note)
			
			# reset the scenes
			self.scenes["hosts_view"]	 = {}
			self.scenes["services_view"] = {}

			try:
				self.services_view.notebook.destroy()
			except: pass
			try:
				self.work.notebook.destroy()
			except: pass

		# set the db location as headerbar subtitle
		self.main.headerbar.set_subtitle(self.engine.database.db_loc)	

		# refresh the hostviews and servicesview
		for host in self.scenes["hosts_view"]:
			self.scenes["hosts_view"][host].refresh(self.engine.database)

		for service in self.scenes["services_view"]:
			self.scenes["services_view"][service].refresh(self.engine.database, view_out_scope = self.main.out_of_scope.get_active())

	def _clear_workspace(self):
		""" 
		remove host_view or services_view notebook
		    and welcome notebook 
		"""

		try:
			self.main.workspace.remove(self.main.welcome_note)
		except: pass
		try:
			self.main.workspace.remove(self.services_view.notebook)
		except: pass
		try:
			self.main.workspace.remove(self.work.notebook)
		except: pass

		
		return True

	def _filter_service(self, service):
		""" function to replace service name """
		service = service.lower()
		service = service.replace("soap","http").replace("https","http").replace("ssl","http").replace("http-proxy","http").replace("http-alt","http").replace("ajp13","http").replace("vnc-http","http").replace("http-mgmt","http").replace("x509","http").replace('iiimsf','http')
		service = service.replace("microsoft-ds","netbios-ssn")
		service = service.replace("imaps","imap").replace("pop3s","pop3").replace("smtps","smtp").replace("pop3pw","pop3")
		service = service.replace("psql","postgresql")

		return service
		
	def _controller_switch(self, widget, test, newpage):
		""" switch from hostview to services view and vice-versa """
		if newpage == 0:
			# switch to host view
			self.on_services_view = False
			
			try:
				self.main.workspace.remove(self.services_view.notebook)
			except:  
				# empty workspace
				self.main.workspace.remove(self.main.welcome_note)

			try:
				self.main.workspace.add(self.work.notebook)	
			except:
				# empty workspace
				self.main.workspace.add(self.main.welcome_note)

		
		elif newpage == 1:
			# switch to servies view
			
			self.on_services_view = True
			
			try:
				self.main.workspace.remove(self.work.notebook)
			except: 
				# empty workspace
				self.main.workspace.remove(self.main.welcome_note)

			try:
				self.main.workspace.add(self.services_view.notebook)
			except: 
				# empty workspace
				self.main.workspace.add(self.main.welcome_note)
		
		# clear the mouse_click menu
		try:
			self.rightclickmenu.destroy()
		except: pass

	def _scope(self, widget, add, targets):
		""" add / remove host scope """

		for host_obj in targets:
			self.engine.database.switch_scope(add, host_obj)

		self._sync()


	def _showhide_scope(self, widget):
		""" show / hide out-of-scope targets """
		self.host_list.toggle_scope()
		self.services_list.toggle_scope()

		self._sync() #reset=True)


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
			
			if self.add_window.hostdiscovery.get_active():
				# user chose to scan the new host
				# we will add it using the run_ext function
				# using all the accrocco
				active = self.add_window.nmap_combo.get_active()
				model  = self.add_window.nmap_combo.get_model()

				button_workaround = Gtk.Button()
				button_workaround.set_label(model[active][0])

				self.run_extra( button_workaround, target, self.engine.get_extension("shell"), "hostlist", model[active][0] )
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
		self.add_window = Targetadd(self.engine.database)
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
				self.engine = karmaEngine(session_file=file_selected)

				# update the hostlist
				self._clear_workspace()
				self._sync(reset=True)
				
			except Exception as e:
				print (e) 
			
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()


		

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
				shutil.copy(self.engine.database.db_loc, file_selected)
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

			self.engine.import_file(file_selected)

			self._sync()

			
		elif response == Gtk.ResponseType.CANCEL:
			dialog.destroy()

		dialog.destroy()
		


	def _delete_host(self, widget, hosts):
		""" Delete host from database """

		# ask for confirmation with a dialog
		dialog = Gtk.MessageDialog(self.main.window, 0, Gtk.MessageType.WARNING,
			Gtk.ButtonsType.OK_CANCEL, "Delete host(s)?")
		dialog.format_secondary_text(
			"This operation will be irreversible.")
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			dialog.close()

			for host in hosts:

				self.engine.database.remove_host(host.id)

				if host == self.work.host:
					# Remove host from the workspace
					self._clear_workspace()
					self.main.workspace.add(self.main.welcome_note)


				model = self.host_list.hosttree.get_model()

				for row in model:
					if row[4] == host.id:
						self.host_list.host_liststore.remove(row.iter)

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
			self.services_view = Serviceview(selected_service, self.engine.database, view_out_scope=self.main.out_of_scope.get_active())
			self.scenes["services_view"][str(cell)] = self.services_view

		# add the scene
		self._selected_opt["service"] = self.services_view.service
		self.main.workspace.add(self.services_view.notebook)

		self.services_view.treeview.connect("button_press_event", self.mouse_click)


	def _history_activated(self, listbox, cell, listboxrow):

		(model, pathlist) = self.work.history_view.get_selection().get_selected_rows()
		for path in pathlist :

			tree_iter = model.get_iter(path)
			log_id   = model.get_value(tree_iter,0)

			self.logger.open_log(log_id)	



	def on_row_activated(self, listbox, cell, listboxrow):
		""" Generate the treeView for the ports """

		self._clear_workspace()

		(model, pathlist) = self.host_list.hosttree.get_selection().get_selected_rows()
		for path in pathlist :

			tree_iter = model.get_iter(path)
			host_id = model.get_value(tree_iter,5) # selected host address

			if str(host_id) in self.scenes["hosts_view"]:
				# check if the scene was already loaded
				self.work = self.scenes["hosts_view"][str(host_id)]

			else: 
				# generate the scene
				db_host = self.engine.database.get_host(host_id)
				self.work = Hostview(db_host, self.engine.database)

				# connect the history view to click event
				self.work.history_view.connect("row-activated", self._history_activated)

				self.scenes["hosts_view"][str(host_id)] = self.work

		# add the scene
		self._selected_opt["host"]   = self.work.host.address
		self._selected_opt["domain"] = self.work.host.hostname
		self.main.workspace.add(self.work.notebook)

		self.work.treeview.connect("button_press_event", self.mouse_click)


	def run_extra(self, widget, target, ext, service, sub_item):
		""" Called on adding new hosts """

		try: self._temp_win.destroy()
		except: pass

		view, pid, id = self.engine.start_task(ext.name, sub_item, target, karmaconf={"autoexec":True, "proxychains":False})
		view.show()

		self._temp_win = Gtk.Window() # ugly fix for tasks termination
		self._temp_win.add(view)

		self.logger.add_log(pid , sub_item, target, ext.name, id)
			


	def run_multi_extra(self, widget, targets, ext, service, sub_item):
		""" run extension against multiple targets """

		for serv in targets:

			try:
				# targeting service
				address = serv.host.address
				port = serv.port
				protocol = serv.protocol
			except:
				# targeting host
				address = serv.address
				protocol = "tcp"
				port = 0

			view, pid, id = self.engine.start_task(ext.name, sub_item, address, rport=port, proto=protocol, service_str=service, karmaconf={"autoexec":self.main.auto_exec.get_active(), "proxychains":self.main.use_proxychains.get_active()})
			view.show()
			#self.tasks[id] = { "views" : view, "ext" : ext }
			self.logger.add_log(pid , sub_item, address, ext.name, id)
			
			# box label + close button for extension
			box_label = Gtk.Box(spacing=6)
			box_label.add( Gtk.Label(sub_item) )
			close_image = Gtk.Image.new_from_icon_name( "gtk-delete", Gtk.IconSize.MENU )
			close_button = Gtk.Button()
			close_button.set_relief(Gtk.ReliefStyle.NONE)
			close_button.add(close_image)
			box_label.add( close_button )

			# close task window option
			close_button.connect("clicked", self.close_task_tab, view)

			if self.on_services_view:
				self.services_view.notebook.append_page(view,box_label)
				self.services_view.notebook.set_current_page(-1)
			else:
				self.work.notebook.append_page(view,box_label)
				self.work.notebook.set_current_page(-1)

			box_label.show_all()


	def host_click(self, tv, event):
		""" right click on a host event """
		
		# grab the right click
		if event.button == 3:

			rightclickmenu = Gtk.Menu()

			# get selected host
			try:
				targets = []

				(model, pathlist) = self.host_list.hosttree.get_selection().get_selected_rows()
				
				if len(pathlist) < 1:
					# right click on nothing
					return False 

				for path in pathlist :
					# Fill target's array

					tree_iter = model.get_iter(path)

					address = model.get_value(tree_iter,1) # selected host address
					domain = model.get_value(tree_iter,2) # selected host address
					host_id = model.get_value(tree_iter,5)

					host_obj = self.engine.database.get_host(host_id)

					targets.append(host_obj)

					self._selected_opt["host"] = address
					self._selected_opt["domain"] = domain
					self._selected_opt["port"] = 0

					# set hosts generic shell conf section
					extra_name = "hostlist"

					# Delete host option
					i4 = Gtk.MenuItem("Delete")
					i4.show()

					rightclickmenu.append(i4)
					i4.connect("activate", self._delete_host, targets)

				if len(targets) > 1:
					# multiple hosts selected
					# we will add both remove and add to scope options
					i5 = Gtk.MenuItem("Remove Scope")
					i6 = Gtk.MenuItem("Add Scope")

					i5.show()
					i6.show()

					rightclickmenu.append(i5)
					rightclickmenu.append(i6)

					i5.connect("activate", self._scope, False, targets) # True means Add
					i6.connect("activate", self._scope, True, targets) # False means remove

				else:
					# single host selected
					# check if the host in scope and add only one option
					if host_obj.scope:
						# in scope
						i5 = Gtk.MenuItem("Remove Scope")
						i5.connect("activate", self._scope, False, targets) # False means remove

					else:
						# Out of scope item
						i5 = Gtk.MenuItem("Add Scope")
						i5.connect("activate", self._scope, True, targets) # True means Add
						
					i5.show()
					rightclickmenu.append(i5)

				extra = self.engine.get_menu(extra_name)

				for c_ext in extra:
					
					try:
						tabs = {}
						#extension_ext_menu = Gtk.Menu()
						submenu = extra[c_ext].submenu(extra_name)

						for sub_item in submenu:
							#print(sub_item)
							if len(sub_item.split("/")) > 1:
								prev = ""
								prevst = ""

								for sub in sub_item.split("/"):
									if sub != sub_item.split("/")[-1]:
									
										# new category
										t_menu = Gtk.Menu()
										t = Gtk.MenuItem(sub)
										t.show()
										t.set_submenu(t_menu)

										if not sub in tabs:
											
											tabs[sub] = t_menu

											if prevst != "":
												prev.append(t)
											else:
												rightclickmenu.append(t)
										
										prev = tabs[sub]
										prevst = sub

									else:
										#print(sub)
										item = Gtk.MenuItem( sub ) 
										item.show()
										item.connect('activate', self.run_multi_extra, targets, extra[c_ext], extra_name, sub_item)

										prev.append(item)


							else:
								# extension in any sub-categories
								item = Gtk.MenuItem(sub_item)
								rightclickmenu.append(item)
								
								# show and connect the extension
								item.show()
								item.connect('activate', self.run_multi_extra, targets, extra[c_ext], extra_name, sub_item)

					except Exception as e : 
						if self.on_services_view:
							item = Gtk.MenuItem(c_ext)
							item.show()
							rightclickmenu.append(item)

							item.connect("activate", self.run_multi_extra, targets, extra[c_ext], service, c_ext)


				rightclickmenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
				rightclickmenu.show_all()

				return True

			except Exception as e: print(e)



	def mouse_click(self, tv, event, alltargets=False):
		""" right click on a service event """
		
		if event.button == 3:

			# create the menu and submenu objects
			rightclickmenu          = Gtk.Menu()
			
			targets = []
			generic = []

			# check
			if self.on_services_view:
				if alltargets:
					(model, pathlist) = self.services_list.servicestree.get_selection().get_selected_rows()
				else:
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

					if self.on_services_view:
						if alltargets:
							service = self._filter_service(model.get_value(tree_iter,0)) # selected service
							# set shell conf section from user selection
							self._selected_opt["service"] =  service

							for port in self.engine.database.get_ports_by_service(service):
								targets.append(port)
						else:
							# set selected port
							selected_port = model.get_value(tree_iter,1) 
							self._selected_opt["port"] = selected_port 

							# set selected host if on service view
							self._selected_opt["host"] =  model.get_value(tree_iter,4) 
							targets.append(self.engine.database.get_port(model.get_value(tree_iter,7) ))

					else:
						# set selected port
						selected_port = model.get_value(tree_iter,1) 
						self._selected_opt["port"] = selected_port 

						# set selected service if not on service view
						selected_service = model.get_value(tree_iter,4) # selected service
						targets.append(self.engine.database.get_port(model.get_value(tree_iter,7)))
						self._selected_opt["service"] = selected_service 

			except Exception as e:
				print(e)
				pass
			
			#print('si')
			# fix some multiple names
			self._selected_opt["service"] = self._filter_service(self._selected_opt["service"])

			# get extra extensions
			extra = self.engine.get_menu(self._selected_opt["service"])

			for extension in extra:
				if extension == "shell":
					# little trick for shell ext
					iE = Gtk.MenuItem(self._selected_opt["service"])
				else:
					iE = Gtk.MenuItem(extension)

				iE.show()
				rightclickmenu.append(iE)

				# check if there is a submenu for the current extension
				try:
					tabs = {}
					extension_ext_menu = Gtk.Menu()
					submenu = extra[extension].submenu(self._selected_opt["service"])

					for sub_item in submenu:
						#print(sub_item)
						if len(sub_item.split("/")) > 1:
							prev = ""
							prevst = ""

							for sub in sub_item.split("/"):
								if sub != sub_item.split("/")[-1]:
								
									# new category
									t_menu = Gtk.Menu()
									t = Gtk.MenuItem(sub)
									t.show()
									t.set_submenu(t_menu)

									if not sub in tabs:
										
										tabs[sub] = t_menu

										if prevst != "":
											prev.append(t)
										else:
											extension_ext_menu.append(t)
									
									prev = tabs[sub]
									prevst = sub

								else:
									#print(sub)
									item = Gtk.MenuItem( sub ) 
									item.show()
									item.connect('activate', self.run_multi_extra, targets, extra[extension], self._selected_opt["service"], sub_item)

									prev.append(item)


						else:
							# extension in any sub-categories
							item = Gtk.MenuItem(sub_item)
							extension_ext_menu.append(item)
							
							# show and connect the extension
							item.show()
							item.connect('activate', self.run_multi_extra, targets, extra[extension], self._selected_opt["service"], sub_item)

					if len(tabs) == 0:
						not_found = Gtk.MenuItem("nothing")
						not_found.show()
						extension_ext_menu.append(not_found)
					
					iE.set_submenu(extension_ext_menu)

				except Exception as e:
					#print(e)
					iE.connect('activate', self.run_multi_extra, targets, extra[extension], self._selected_opt["service"], extra[extension].menu["label"]) #.menu["label"])

				try:
					# try if there is generic for the current extension
					submenu = extra[extension].submenu("generic")

					for sub_item in submenu:
						# remove _ and show spaces
						generic.append(sub_item.replace("_"," "))
				except: pass

			separator = Gtk.SeparatorMenuItem()
			separator.show()
			rightclickmenu.append(separator)

			gen_x = self.engine.get_menu("generic")

			for gen in generic:

				i2 = Gtk.MenuItem(gen)
				i2.show()
				rightclickmenu.append(i2)

				i2.connect("activate", self.run_multi_extra, targets, extra["shell"], "generic", gen)

			rightclickmenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

			return True

	def end_task(self, caller, id, out):
		""" function called when an extension's finish a task """

		self.logger.complete_log(id, out) # complete the logger row of the task
		#del self.tasks[id] # delete the task from the running task's dict

		self._sync()
		


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
