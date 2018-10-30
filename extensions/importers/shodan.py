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
import json

class karma_ext():

	def __init__(self, database):
		self.name     = "shodan.io importer"
		self.database = database
	
	def match(self, head_str):
		""" match string in order to identify nmap xml report """
		if ", \"postal_code\": " in head_str:
			return True
		return False

	def parse(self, json_file):
		""" import smap.py json output """

		file = open(json_file,'r')
		sp_out = file.read()
		file.close()

		smap_out = json.loads(sp_out)

		for host in smap_out:
			# get the os match

			if smap_out[host]["os"]:
				match = smap_out[host]["os"]
			else:
				match = ""

			# get the first hostname
			try:
				hostname = smap_out[host]["hostnames"][0]
			except:
				hostname = ""

			# check if the host is already in the db
			if self.database.host_exist(host):
				# update
				add_host = self.database.session.query(targets).filter( targets.address == host ).one()
				
				# update values only if there's more informations

				if len(hostname) > 0:
					if not hostname in add_host.hostname:
						# add multiple hostnames
						add_host.hostname = add_host.hostname + " " + hostname

				if len(match) > 0:
					add_host.os_match = match
				if len(add_host.status) > 0:
					add_host.status = "up"

				add_host.isp = smap_out[host]["isp"]
				add_host.country_name =  smap_out[host]["country_name"]
				add_host.country_code = smap_out[host]["country_code"]
				add_host.organization = smap_out[host]["org"]
				add_host.latitude = smap_out[host]["latitude"]
				add_host.longitude = smap_out[host]["longitude"]


			else:
				# add the host to the db
				add_host = targets(address=host, latitude=smap_out[host]["latitude"],longitude= smap_out[host]["longitude"],hostname=hostname, os_match=match, status="up", country_code = smap_out[host]["country_code"], country_name = smap_out[host]["country_name"], organization = smap_out[host]["org"], isp = smap_out[host]["isp"])
			
			# commit to db
			self.database.session.add(add_host)
			self.database.session.commit()

			i = 0


			for port in smap_out[host]["ports"]:

				service = self.database._find_nmap_service(port,smap_out[host]["data"][i]["transport"])

				if self.database.port_exist(add_host.id, port, smap_out[host]["data"][i]["transport"]):
					# update the existing port
					add_port = self.database.session.query(services).filter( services.host_id == add_host.id, services.port == port, services.protocol == smap_out[host]["data"][i]["transport"] ).one()

					if len(service) > 0:
						add_port.service = service



				else:
					# add the new port
					add_port = services(port=port, protocol=smap_out[host]["data"][i]["transport"], service=service, fingerprint="", state="open", banner="", host = add_host)

				# commit to db
				self.database.session.add(add_port)

				i += 1

		self.database.session.commit()
