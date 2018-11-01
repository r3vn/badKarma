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

# icons lib
import gi
import os
gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf
from gi.repository import Gtk

# OS ICONS
def icon(typed):
	return GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/"+typed+"-icon.png",width=24, height=24, preserve_aspect_ratio=True)

def icon_lg(typed):
	return GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/"+typed+"-icon.png",width=64, height=64, preserve_aspect_ratio=True)


# PORTS STATE ICONS
def port_open_icon():
	return GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/open.gif",width=14, height=14, preserve_aspect_ratio=True)

def port_filtered_icon():
	return 	GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/filtered.gif",width=14, height=14, preserve_aspect_ratio=True)

def port_closed_icon():
	return 	GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/closed.gif",width=14, height=14, preserve_aspect_ratio=True)

# GTK Stock icons
def gtk_exit_fullscreen(image):
	return image.set_from_stock(Gtk.STOCK_LEAVE_FULLSCREEN, Gtk.IconSize.LARGE_TOOLBAR)

def gtk_fullscreen(image):
	return image.set_from_stock(Gtk.STOCK_FULLSCREEN, Gtk.IconSize.LARGE_TOOLBAR)

# get os icons based on string match
def get_icon(os, lg=False):

	os = os.lower()

	if lg:
		icon_func = icon_lg
	else:
		icon_func = icon

	# overwrite linux
	if "android" in os:
		return icon_func("android")

	if "ios" in os:
		return icon_func("ios")

	
	if "linux" in os:
		return icon_func("linux")

	elif "windows" in os:
		return icon_func("windows")

	elif "solaris" in os:
		return icon_func("solaris")

	elif "freebsd" in os:
		return icon_func("freebsd")

	elif "openbsd" in os:
		return icon_func("openbsd")

	elif "macos" in os:
		return icon_func("macosx")

	elif "unix" in os:
		return icon_func("unix")

	else:
		return icon_func("unknown")