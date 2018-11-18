#!/usr/bin/env python3
#coding=utf-8
# vim: set filetype=python ts=4 sw=4 sts=4 expandtab autoindent :

'''
Get username and password from http://www.bugmenot.com/

File: bugmynot.py
Original Author: notsobad.me
Python3 port + new regex: @r3vn /badKarma

'''

import optparse
import sys
import urllib.request
import re
import json

class BugMeNot:
	def __init__(self):
		self.regex = u'<dl><dt>Username:</dt><dd><kbd>([^<]*)</kbd></dd>'
		self.regex += u'<dt>Password:</dt><dd><kbd>([^<]*)</kbd></dd>'
		self.regex += u'<dt class="stats">Stats:</dt><dd class="stats"> <ul> <li class="[^"]* [^"]*">([0-9]*%)[^<]*</li>'

	def _get_account(self, host):
		headers = dict()
		headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
		headers['Pragma'] = 'no-cache'
		headers['Cache-Control'] = 'no-cache'

		try:
			request = urllib.request.Request('http://www.bugmenot.com/view/%s' % host, None, headers)

			page = urllib.request.urlopen(request).read().decode() 
            
		except Exception as e:
			print(e)
			print ('Http Error! Please check the url you input and the network connection')
			sys.exit()

		re_loginpwd = re.compile(self.regex, re.IGNORECASE | re.DOTALL)

		match = re_loginpwd.findall(page)
	
		return [{'username':i, 'password':j, 'stats':s} for i, j, s in match if i and j and len(i) < 30]

	def get_account(self, host):
		return self._get_account(host)


if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option("-s", "--site", dest="site", help="The target site")
	parser.add_option("-t", "--ret_type", dest="ret", default="text", help="The return type(text/json)")

	(options, args) = parser.parse_args()

	if options.site:
		bug = BugMeNot()
		accounts = bug.get_account(options.site)
		if not accounts:
			print ("No accounts/password for %s found in www.bugmenot.com" % options.site)
			sys.exit(1)

		if options.ret == 'text':
			print ("%-30s\t%-20s\t%-5s" % ("Username", "Password", "Success"))
			line_len = 70

			print ("-" * line_len)
			for account in accounts:
				print ("%(username)-30s\t%(password)-20s\t%(stats)-5s" % account)

		elif options.ret == 'json':
			
			print (json.dumps(accounts))
	else:
		parser.print_help()
		sys.exit()

	sys.exit()
