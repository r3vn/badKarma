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

from core.database import *
from xml.etree import ElementTree

import json

class karma_ext():

	def __init__(self, database):
		self.name     = "masscan importer"
		self.database = database
	
	def match(self, head_str):
		""" match string in order to identify nmap xml report """
		if "masscan" in head_str.lower():
			return True
		return False

	def parse(self, xml):
		""" import masscan xml output """

		dom = ElementTree.parse(xml)
		scan = dom.findall('host')
		out = {}
		add_host = ""

		for s in scan:
			addr = s.getchildren()[0].items()[0][1]
			port = s.getchildren()[1].getchildren()[0].items()[1][1]

			try:
				service = s.getchildren()[1].getchildren()[0].getchildren()[1].items()[0][1]
			except: 
				service = ""
			try:
				banner = s.getchildren()[1].getchildren()[0].getchildren()[1].items()[1][1]
			except: 
				banner = ""
			try:
				port_state =  s.getchildren()[1].getchildren()[0].getchildren()[0].items()[0][1]
			except:
				port_state = ""

			try:
				proto = s.getchildren()[1].getchildren()[0].items()[0][1]
			except: 
				proto= ""


			if addr in out:
				if service != "title" and service != "":

					if self.database.port_exist(add_host.id, port, proto):
						# update the existing port
						add_port = self.database.session.query(services).filter( services.host_id == add_host.id, services.port == port, services.protocol == proto ).one()

						if len(service) > 0:
							add_port.service = service
						#if len(service.servicefp) > 0:
						#	add_port.fingerprint = str(service.servicefp)

						if len(port_state) > 0:
							add_port.state = port_state
						if len(banner) > 0:
							add_port.banner = banner

					else:
						# add the new port
						add_port = services(port=port, protocol=proto, service=service, fingerprint=banner, state=port_state, banner="", host = out[addr])

						# commit to db
						self.database.session.add(add_port)

			else:
				if self.database.host_exist(addr):

					add_host = self.database.session.query(targets).filter( targets.address == addr ).one()

				else:
					# add the host to the db
					add_host = targets(address=addr, status="up")
					
					# commit to db
					self.database.session.add(add_host)

				out[addr] = add_host

			self.database.session.commit()
			

	def parse_json(self, json_file):
		""" 
		broken json importer, seems like python 3 json parser doesn't like
		 masscan's json output for some reason :/
		"""

		file = open(json_file,'r')
		sp_out = file.read()
		file.close()

		#print s

		masscan_out = json.loads(sp_out.replace('\0', ''))


		for line in masscan_out:

			if self.database.host_exist(line["ip"]):

				add_host = self.database.session.query(targets).filter( targets.address == line["ip"] ).one()

			else:
				# add the host to the db
				add_host = targets(address=line["ip"], status="up")
				
				# commit to db
				self.database.session.add(add_host)

				#out[addr] = add_host

			for port in line["ports"]:
				if self.port_exist(add_host.id, port["port"], port["proto"]):

					# update the existing port
					add_port = self.database.session.query(services).filter( services.host_id == add_host.id, services.port == port["port"], services.protocol == port["proto"] ).one()

					try:
						if len(port["status"]) > 0:
							add_port.state = port["status"]

						if len(port["service"]["name"]) > 0:
							add_port.service = port["service"]["name"]

						if len(port["service"]["banner"]) > 0:
							add_port.fingerprint = banner


					except:
						pass

				else:
					# add the new port
					add_port = services(port=port["port"], protocol=port["proto"], service=port["service"]["name"], fingerprint=port["service"]["banner"], state=port["status"], banner="", host = line["ip"])

					# commit to db
					self.database.session.add(add_port)

				self.database.session.commit()



