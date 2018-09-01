# icons lib
import gi
import os
gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf

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