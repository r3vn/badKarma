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
#
# File contributed by Eugenio "g7" Paolantonio
#

import os

from distutils.core import setup

def asset_walk(directory, target_prefix, root_replace=None):
	"""
	Walks through the specified directory and returns a distutils-compilant
	tuple ready to be appended to data_files.

	:param: directory: the directory to scan
	:param: target_prefix: the prefix to append to the target directory
	:param: root_replace: if != None, replaces the initial directory name with the
	specified replacement. Note that the replacement is pretty lazy.
	:returns: a tuple in the following format: ("%(target_prefix)s/%(directory)s", [files...])
	"""

	if os.path.isabs(directory):
		raise Exception("directory must be a relative path")

	return [
		(
			os.path.join(
				target_prefix,
				(
					root.replace(
						directory,
						root_replace
					)
					if root_replace is not None
					else root
				)
			),
			[
				os.path.join(root, file_)
				for file_ in files
			]
		)
		for root, directories, files in os.walk(directory)
		if files
	]

setup(
	name="badKarma",
	version="0.0.1",
	description="network reconnaissance toolkit",
	author="Giuseppe Corti",
	url="https://github.com/r3vn/badKarma",
	scripts=["badkarma.py"],
	packages=[
		"core",
		"extensions",
	],
	data_files= [
			("/usr/share/applications", ["extra/badkarma.desktop"]),
		] + \
		asset_walk("extra/hicolor", "/usr/share/icons", root_replace="hicolor") + \
		asset_walk("assets", "/usr/share/badkarma") + \
		asset_walk("conf", "/usr/share/badkarma") + \
		asset_walk("scripts", "/usr/share/badkarma") + \
		asset_walk("wordlists", "/usr/share/badkarma"),
	requires=[
		"libnmap",
		"sqlalchemy",
		"shodan",
		"gi",
	]
)
