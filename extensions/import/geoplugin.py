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

from core.database import *
import json

class karma_ext():

	name     = "geoplugin importer"
			
	def match(self, head_str):
		""" match string in order to identify nmap xml report """
		if "geoplugin_request" in head_str:
			return True
		return False

	def parse(self, json_file, database):
		""" import host's longitude and latitude from geoplugin json """
		file = open(json_file,'r')
		sp_out = file.read()
		file.close()

		geo_out = json.loads(sp_out)

		# check if the host exists
		if database.host_exist(geo_out["geoplugin_request"]):
			# update
			add_host = database.session.query(targets).filter( targets.address == geo_out["geoplugin_request"] ).one()
				
			# update values only if there's more informations
			
			add_host.latitude = geo_out["geoplugin_latitude"]
			add_host.longitude = geo_out["geoplugin_longitude"]
			add_host.country_code = geo_out["geoplugin_countryCode"]
			add_host.country_name = geo_out["geoplugin_countryName"]

			database.session.add(add_host)
			database.session.commit()
