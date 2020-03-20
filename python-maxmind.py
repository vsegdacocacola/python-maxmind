#!/usr/bin/env python

import geoip2.database
import sys
import re

ip = None

delimiter = '\t'

folder = '/var/lib/GeoIP/' # Folder, where MaxMind mmdb files are stored

filenames = { \
    'country' : 'GeoLite2-Country.mmdb', \
    'city' : 'GeoLite2-City.mmdb',  \
    'asn' : 'GeoLite2-ASN.mmdb' \
} # List of mmdb file names

#Initialize mmdb readers

readers = {}

for key in filenames.keys():
    path = folder + filenames[key]
    readers[key] = geoip2.database.Reader(path)

lines = sys.stdin.readlines()

for line in lines:
    if(line):
        m = re.match(r'([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})', line)
        if(m): 
            ip = m.group()
            result = { 'ip' : ip, 'city' : '', 'country' : '', 'asn' : '' }
            #Call corresponding method
            for key in readers.keys():
                func = getattr(readers[key] ,key)
                result[key] = func(ip)

            response = result['ip']
            
            if hasattr(result['country'],'country'):
                if hasattr(result['country'].country, 'isocode'):
                    response += delimiter + result['country'].country.iso_code
                else:
                    response += delimiter
                if hasattr(result['country'].country, 'names') and ('en' in result['country'].country.names):
                    response += delimiter + result['country'].country.names['en']
                else:
                    response += delimiter
            else:
                response += delimiter + delimiter

            if hasattr(result['city'],'names'):
                response += delimiter + result['city'].city.names['en']
            else:
                response += delimiter

            if hasattr(result['asn'],'autonomous_system_number'):
                response += delimiter + str(result['asn'].autonomous_system_number) + delimiter + result['asn'].autonomous_system_organization
            else:
                response += delimiter

            response = line.strip() + delimiter + response
            print(response.encode('utf-8').strip())

for key in readers.keys():
    readers[key].close()

