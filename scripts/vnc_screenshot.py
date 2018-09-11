#!/usr/bin/env python3
# 
#  Gtk Vnc screenshot script
#  Author: BadKarma - Giuseppe `r3vn` Corti

import base64
import gi
import time
import threading
import sys

gi.require_version('GtkVnc', '2.0')

from gi.repository import GtkVnc
from gi.repository import Gtk

def screenshot(dpy):
	# wait to get an image
	time.sleep(5)

	# save the image
	pix = dpy.get_pixbuf()
	pix.savev( "/tmp/badkarma-screenshot"+sys.argv[1]+"-"+sys.argv[2], "png", "", "")

	# return the base64
	with open ("/tmp/badkarma-screenshot"+sys.argv[1]+"-"+sys.argv[2], "rb" ) as image:
		print( base64.b64encode(image.read()).decode() )

	# quit
	Gtk.main_quit()
	quit()		

def vnc_connected(dpy):

	# another workaround in order to get rid of black screenshots
	thread = threading.Thread(target=screenshot,args=[dpy])
	thread.start()

if __name__ == "__main__":
	
	dpy = GtkVnc.Display()
	dpy.open_host(sys.argv[1], sys.argv[2])

	dpy.connect("vnc-initialized", vnc_connected)

	# stupid workaround needed to suppress gdk warnings
	win = Gtk.Window()
	win.show()
	win.hide()
	win.add(dpy)

	Gtk.main()
