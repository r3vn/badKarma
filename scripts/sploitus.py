#!/usr/bin/env python3
import requests, json, sys

q = sys.argv[1]
p = {'offset': 0, 'query': q, 'sort': 'default', 'title': 'false', 'type': 'exploits'}
r = requests.post('https://sploitus.com/search', json=p).text
j = json.loads(r)

print('[!] Sploitus made by @i_bo0om | Full result: https://sploitus.com/?query=' + q + '#exploits')
print('[!] Found: ' + str(j['exploits_total']) + ' results')

for e in j['exploits']:
	print('---\n\t"' + e['title'] + '"\n\t' + e['href'] + '\n\tPublished: ' + e['published'])

print('\n---')

