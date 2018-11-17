#!/usr/bin/env python3
# badKarma - network reconnaissance toolkit
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

import signal
import argparse
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from core.main import Handler
from core.extensions import karmaEngine

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--session', help='Open a session file')
	args = parser.parse_args()

	signal.signal(signal.SIGINT, signal.SIG_DFL)

	if args.session:
		engine = karmaEngine(session_file=args.session)
	else:
		engine = karmaEngine()

	Handler(engine)
	Gtk.main()
