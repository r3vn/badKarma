# icons lib
import gi
import os
gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf

# OS ICONS
def icon(typed):
	return GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/"+typed+"-icon.png",width=24, height=24, preserve_aspect_ratio=True)


# PORTS STATE ICONS
def port_open_icon():
	return GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/open.gif",width=14, height=14, preserve_aspect_ratio=True)

def port_filtered_icon():
	return 	GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/filtered.gif",width=14, height=14, preserve_aspect_ratio=True)

def port_closed_icon():
	return 	GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.dirname(os.path.abspath(__file__)) + "/../assets/images/closed.gif",width=14, height=14, preserve_aspect_ratio=True)


# get os icons based on string match
def get_icon(os):

	os = os.lower()

	# overwrite linux
	if "android" in os:
		return icon("android")

	if "ios" in os:
		return icon("ios")

	
	if "linux" in os:
		return icon("linux")

	elif "windows" in os:
		return icon("windows")

	elif "solaris" in os:
		return icon("solaris")

	elif "freebsd" in os:
		return icon("freebsd")

	elif "openbsd" in os:
		return icon("openbsd")

	elif "macos" in os:
		return icon("macosx")

	elif "unix" in os:
		return icon("unix")

	else:
		return icon("unknown")