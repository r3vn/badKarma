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
from libnmap.parser import NmapParser

class karma_ext():

	def __init__(self, database):
		self.name     = "nmap importer"
		self.database = database
	
	def match(self, head_str):
		""" match string in order to identify nmap xml report """
		match_str = """<nmaprun scanner="nmap" args="nmap"""

		if match_str in head_str.lower():
			return True
		return False


	def parse(self, xml):
		""" import an nmap xml output """

		report = NmapParser.parse_fromfile(xml)

		for host in report.hosts:
			# get os accuracy
			try:
				accuracy = str(host.os_class_probabilities()[0])
			except:
				accuracy = ""

			# get the os match
			try:
				match = str(host.os_match_probabilities()[0])
			except:
				match = ""

			# get the first hostname
			try:
				hostname = host.hostnames[0]
			except:
				hostname = ""

			# check if the host is already in the db
			if self.database.host_exist(host.address):
				# update
				add_host = self.database.session.query(targets).filter( targets.address == host.address ).one()
				
				# update values only if there's more informations
				if len(str(host.scripts_results)) > 3:
					add_host.scripts = str(host.scripts_results)
				if len(hostname) > 0:
					add_host.hostname = hostname
				if len(match) > 0:
					add_host.os_match = match
				if len(accuracy) >0:
					add_host.os_accuracy = accuracy
				if len(host.ipv4) > 0:
					add_host.ipv4 = host.ipv4
				if len(host.ipv6) > 0:
					add_host.ipv6 = host.ipv6
				if len(host.mac) > 0:
					add_host.mac = host.mac
				if len(host.status) > 0:
					add_host.status = host.status
				if len(host.tcpsequence) > 0:
					add_host.tcpsequence = host.tcpsequence
				if len(host.vendor) > 0:
					add_host.vendor = host.vendor
				if len(str(host.uptime)) > 0:
					add_host.uptime = host.uptime
				if len(str(host.lastboot)) > 0:
					add_host.lastboot = host.lastboot
				if len(str(host.distance)) > 0:
					add_host.distance = host.distance

			else:
				# add the host to the db
				add_host = targets(address=host.address,scripts=str(host.scripts_results), hostname=hostname, os_match=match, os_accuracy=accuracy, ipv4=host.ipv4, ipv6=host.ipv6, mac=host.mac, status=host.status, tcpsequence=host.tcpsequence, vendor=host.vendor, uptime=host.uptime, lastboot=host.lastboot, distance=host.distance)
			
			# commit to db
			self.database.session.add(add_host)
			self.database.session.commit()

			for port in host.get_ports():

				service = host.get_service(port[0],port[1])

				if self.database.port_exist(add_host.id, port[0], port[1]):
					# update the existing port
					add_port = self.database.session.query(services).filter( services.host_id == add_host.id, services.port == port[0], services.protocol == port[1] ).one()

					if len(service.service) > 0:
						add_port.service = service.service
					if len(service.servicefp) > 0:
						add_port.fingerprint = str(service.servicefp)
					#print(service.servicefp)

					if len(service.state) > 0:
						add_port.state = service.state
					if len(service.banner) > 0:
						add_port.banner = service.banner

				else:
					# add the new port
					add_port = services(port=port[0], protocol=port[1], service=service.service, fingerprint=service.servicefp, state=service.state, banner=service.banner, host = add_host)

				# commit to db
				self.database.session.add(add_port)

		self.database.session.commit()