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

from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update

from libnmap.parser import NmapParser
from xml.etree import ElementTree

import json

Base = declarative_base()

class targets(Base):
	__tablename__ = "targets"

	id            = Column(Integer, primary_key=True)
	address       = Column(String(50), nullable=False)
	os_match      = Column(Text, nullable=True)
	os_accuracy   = Column(Text, nullable=True)
	ipv4          = Column(String(50), nullable=True)
	ipv6          = Column(String(250), nullable=True)
	mac           = Column(String(50), nullable=True)
	status        = Column(String(50), nullable=True)
	tcpsequence   = Column(String(200), nullable=True)
	hostname      = Column(Text, nullable=True)
	vendor        = Column(Text, nullable=True)
	uptime        = Column(String(100), nullable=True)
	lastboot      = Column(String(100), nullable=True)
	distance      = Column(Integer, nullable=True)
	latitude      = Column(Float, nullable=True)
	longitude     = Column(Float, nullable=True)
	scripts       = Column(Text, nullable=True)

class services(Base):
	__tablename__ = "services"

	id          = Column(Integer, primary_key=True)
	port        = Column(Integer, nullable=False)
	protocol    = Column(String(3), nullable=False)
	service     = Column(String(200), nullable=False)
	fingerprint = Column(Text, nullable=True)
	state       = Column(String(200), nullable=False)
	banner      = Column(Text, nullable=True)
	host        = relationship(targets)
	host_id     = Column(Integer, ForeignKey('targets.id'))

class activity_log(Base):
	__tablename__ = "activity_log"

	id         = Column(Integer, primary_key=True)
	pid        = Column(Integer, nullable=False)
	start_time = Column(String(200), nullable=False)
	end_time   = Column(String(200), nullable=False)
	title      = Column(String(200), nullable=False)
	output     = Column(Text, nullable=True)
	extension  = Column(Text, nullable=True)
	target     = Column(Text, nullable=True)

class notes(Base):
	__tablename__ = "notes"

	id      = Column(Integer, primary_key=True)
	host    = relationship(targets)
	host_id = Column(Integer, ForeignKey("targets.id"))
	title   = Column(String(200))
	text    = Column(Text)

class DB:

	def __init__(self, db_loc="/tmp/badkarma.sqlite"):

		engine = create_engine("sqlite:///"+db_loc)
		Base.metadata.create_all(engine)
		Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)

		self.db_loc = db_loc
		self.session = DBSession()

		# nmap well known services file location
		self.nmap_service_loc = "/usr/share/nmap/nmap-services"


	def _find_nmap_service(self, port, trasport):
		""" search inside nmap well known services file"""

		with open(self.nmap_service_loc,'r') as f:
			for line in f.readlines():
				if str(port)+"/"+trasport in line:

					return line.split()[0]


	def import_geoplugin(self, json_file):
		""" import host's longitude and latitude from geoplugin json """

		file = open(json_file,'r')
		sp_out = file.read()
		file.close()

		geo_out = json.loads(sp_out)

		# check if the host exists
		if self.host_exist(geo_out["geoplugin_request"]):
			# update
			add_host = self.session.query(targets).filter( targets.address == geo_out["geoplugin_request"] ).one()
				
			# update values only if there's more informations
			
			add_host.latitude = geo_out["geoplugin_latitude"]
			add_host.longitude = geo_out["geoplugin_longitude"]

			self.session.add(add_host)
			self.session.commit()




	def import_shodan(self, json_file):
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
			if self.host_exist(host):
				# update
				add_host = self.session.query(targets).filter( targets.address == host ).one()
				
				# update values only if there's more informations

				if len(hostname) > 0:
					add_host.hostname = hostname
				if len(match) > 0:
					add_host.os_match = match
				if len(add_host.status) > 0:
					add_host.status = "up"
				
				add_host.latitude = smap_out[host]["latitude"]
				add_host.longitude = smap_out[host]["longitude"]


			else:
				# add the host to the db
				add_host = targets(address=host, latitude=smap_out[host]["latitude"],longitude= smap_out[host]["longitude"],hostname=hostname, os_match=match, status="up")
			
			# commit to db
			self.session.add(add_host)
			self.session.commit()

			i = 0


			for port in smap_out[host]["ports"]:

				service = self._find_nmap_service(port,smap_out[host]["data"][i]["transport"])

				if self.port_exist(add_host.id, port, smap_out[host]["data"][i]["transport"]):
					# update the existing port
					add_port = self.session.query(services).filter( services.host_id == add_host.id, services.port == port, services.protocol == smap_out[host]["data"][i]["transport"] ).one()

					if len(service) > 0:
						add_port.service = service



				else:
					# add the new port
					add_port = services(port=port, protocol=smap_out[host]["data"][i]["transport"], service=service, fingerprint="", state="open", banner="", host = add_host)

				# commit to db
				self.session.add(add_port)

				i += 1

		self.session.commit()




	def import_masscan(self, xml):
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

					if self.port_exist(add_host.id, port, proto):
						# update the existing port
						add_port = self.session.query(services).filter( services.host_id == add_host.id, services.port == port, services.protocol == proto ).one()

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
						self.session.add(add_port)

			else:
				if self.host_exist(addr):

					add_host = self.session.query(targets).filter( targets.address == addr ).one()

				else:
					# add the host to the db
					add_host = targets(address=addr, status="up")
					
					# commit to db
					self.session.add(add_host)

				out[addr] = add_host

			self.session.commit()
			


	def import_nmap(self, xml):
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
			if self.host_exist(host.address):
				# update
				add_host = self.session.query(targets).filter( targets.address == host.address ).one()
				
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
			self.session.add(add_host)
			self.session.commit()

			for port in host.get_ports():

				service = host.get_service(port[0],port[1])

				if self.port_exist(add_host.id, port[0], port[1]):
					# update the existing port
					add_port = self.session.query(services).filter( services.host_id == add_host.id, services.port == port[0], services.protocol == port[1] ).one()

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
				self.session.add(add_port)

		self.session.commit()

	def add_note(self, host_id, title, text):
		""" add a note """
		add_note = notes(host_id=host_id, title=title, text=text)

		self.session.add(add_note)
		self.session.commit()

		return title, self.session.query(notes).order_by(notes.id.desc()).first().id

	def add_host(self, address):
		""" add a host without scan it """
		add_host = targets(address=address)

		self.session.add(add_host)
		self.session.commit()

	def add_log(self, pid, start_dat, end_dat, title, target, output, extension):
		""" add activity log entry to the database """

		log_add = activity_log( pid=pid, start_time=start_dat, end_time = end_dat, title=title, output=output, extension = extension, target = target )
		self.session.add(log_add)
		self.session.commit()

		return self.get_log_id()

	def save_note(self, note_id, value):

		note = self.session.query(notes).filter( notes.id == note_id ).one()
		note.text=value
		self.session.commit()

	def host_exist(self, ipv4):
		# function to check if a host is already in the databse
		if len(self.session.query(targets).filter( targets.address == ipv4 ).all()) > 0:
			return True
		
		return False

	def port_exist(self, host_id, port, protocol):
		# function to check if a port is already in the database
		if len(self.session.query(services).filter( services.host_id == host_id, services.port == port, services.protocol == protocol ).all()) > 0:
			return True
		
		return False

	def get_note(self, note_id):
		return self.session.query(notes).filter( notes.id == note_id ).one()

	def get_notes(self, host_id):
		return self.session.query(notes).filter( notes.host_id == host_id ).all()

	def get_hosts(self):
		return self.session.query(targets).all()

	def get_host(self, id):
		return self.session.query(targets).filter( targets.id == id ).one()

	def get_port(self,id):
		return self.session.query(services).filter( services.id == id ).one()

	def get_service(self, id):
		return self.session.query(services).filter( services.service == id ).all()

	def get_services_uniq(self):
		return self.session.query(services.service).distinct()

	def get_ports_by_service(self, service):
		return self.session.query(services).filter( services.service == service ).all()

	def get_ports_by_host(self, host):
		return self.session.query(services).filter( services.host == host ).all()


	def get_logs(self, id=''):
		if id == '':
			return self.session.query(activity_log).all()
		
		return self.session.query(activity_log).filter( activity_log.id == int(id) ).one()

	def get_history(self, host):
		return self.session.query(activity_log).filter( activity_log.target.like("%"+host.address+"%") | activity_log.target.like("%"+host.hostname+"%") ).all()

	def get_log_id(self):
		return self.session.query(activity_log).order_by(activity_log.id.desc()).first().id

	def remove_log(self,id):
		todel = self.session.query(activity_log).filter( activity_log.id == id ).one()
		self.session.delete(todel)
		self.session.commit()

		return True

	def remove_note(self, id):
		id = int(id)
		todel = self.session.query(notes).filter( notes.id == id ).one()

		self.session.delete(todel)
		self.session.commit()

		return True


	def remove_host(self, id):
		#print(address)
		todel = self.session.query(targets).filter( targets.id == id ).one()
		todel_2 = self.session.query(services).filter( services.host_id == id ).all()

		self.session.delete(todel)
		for to in todel_2:
			self.session.delete(to)

		self.session.commit()


		return True
