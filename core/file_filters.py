import gi
from gi.repository import Gtk

def add_filter_database(dialog):
	filter_text = Gtk.FileFilter()
	filter_text.set_name("BadKarma sqllite project")
	filter_text.add_mime_type("application/x-sqlite3")
	dialog.add_filter(filter_text)

	filter_any = Gtk.FileFilter()
	filter_any.set_name("Any files")
	filter_any.add_pattern("*")
	dialog.add_filter(filter_any)

  
def add_filter_nmap(dialog):
	filter_text = Gtk.FileFilter()
	filter_text.set_name("nmap XML files")
	filter_text.add_mime_type("text/xml")
	dialog.add_filter(filter_text)

	filter_any = Gtk.FileFilter()
	filter_any.set_name("Any files")
	filter_any.add_pattern("*")
	dialog.add_filter(filter_any)


def add_filter_txt(dialog):
	filter_text = Gtk.FileFilter()
	filter_text.set_name("text TXT files")
	filter_text.add_mime_type("text/txt")
	dialog.add_filter(filter_text)

	filter_any = Gtk.FileFilter()
	filter_any.set_name("Any files")
	filter_any.add_pattern("*")
	dialog.add_filter(filter_any)