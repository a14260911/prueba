import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urlparse
from urllib.parse import urljoin


import logging
import sys

if sys.version_info[0] >= 3:
    # python3
    from configparser import ConfigParser
else:
    # python2.7
    from ConfigParser import ConfigParser



class EdgeRc(ConfigParser):
    def __init__(self, filename):
        ConfigParser.__init__(self, {'client_token': '', 'client_secret':'', 'host':'', 'access_token':'','max_body': '131072', 'headers_to_sign': 'None'})
        logger.debug("loading edgerc from %s", filename)

        self.read(filename)

        logger.debug("successfully loaded edgerc")

    def optionxform(self, optionstr):
        """support both max_body and max-body style keys"""
        return optionstr.replace('-', '_')

    def getlist(self, section, option):
        """
            returns the named option as a list, splitting the original value
            by ','
        """
        value = self.get(section, option)
        if value:
            return value.split(',')
        else:
            return None

logger = logging.getLogger(__name__)

edgerc = EdgeRc('~/.edgerc')
section = "default"
"""
host = edgerc.get(section, 'host')
print (host)
baseurl = 'https://%s' % edgerc.get(section, 'host')
print (baseurl)

s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
result = s.get(urljoin(baseurl, '/diagnostic-tools/v2/ghost-locations/available'))
print (result.status_code)
print (result.json()['locations'][0]['value'])
"""
