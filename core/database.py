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
		try:
			return self.session.query(activity_log).filter( activity_log.target.contains(host.address) | activity_log.target.contains(host.hostname.split(" ")[1]) ).all() # split FIXME
		except:
			return self.session.query(activity_log).filter( activity_log.target == host.address ).all()


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


	def rename_note(self, id, newname):
		toren = self.session.query(notes).filter( notes.id == id ).one()
		toren.title = newname

		self.session.commit()

		return True
