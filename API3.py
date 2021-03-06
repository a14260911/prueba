#! /usr/bin/env python3

""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

#
# usage: verify_creds.py [-h] [--verbose] [--debug] 
#        [--config_file CONFIG_FILE] [--config_section CONFIG_SECTION]
#

import requests, logging, json, sys, os
from random import randint
#from http_calls import EdgeGridHttpCaller
from config import EdgeGridConfig
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig

if sys.version_info[0] >= 3:
     # python3
     from urllib import parse
else:
     # python2.7
     import urlparse as parse


logger = logging.getLogger(__name__)

class EdgeGridHttpCaller():
    def __init__(self, session, debug, verbose, baseurl):
        self.debug = debug
        self.verbose = verbose
        self.session = session
        self.baseurl = baseurl
        return None
   
    def urlJoin(self, url, path):
        return parse.urljoin(url, path)
 
    def getResult(self, endpoint, parameters=None):
      path = endpoint
      endpoint_result = self.session.get(parse.urljoin(self.baseurl,path), params=parameters)
      if self.verbose: print (">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n")
      status = endpoint_result.status_code
      if self.verbose: print( "LOG: GET %s %s %s" % (endpoint,status,endpoint_result.headers["content-type"]))
      self.httpErrors(endpoint_result.status_code, path, endpoint_result.json())
      return endpoint_result.json()
    
    def httpErrors(self, status_code, endpoint, result):
      if not isinstance(result, list):
      	details = result.get('detail') or result.get('details') or ""
      else:
        details = ""
      if status_code == 403:
                    error_msg =  "ERROR: Call to %s failed with a 403 result\n" % endpoint
                    error_msg +=  "ERROR: This indicates a problem with authorization.\n"
                    error_msg +=  "ERROR: Please ensure that the credentials you created for this script\n"
                    error_msg +=  "ERROR: have the necessary permissions in the Luna portal.\n"
                    error_msg +=  "ERROR: Problem details: %s\n" % details
                    exit(error_msg)
      
      if status_code in [400, 401]:
                    error_msg =  "ERROR: Call to %s failed with a %s result\n" % (endpoint, status_code)
                    error_msg +=  "ERROR: This indicates a problem with authentication or headers.\n"
                    error_msg +=  "ERROR: Please ensure that the .edgerc file is formatted correctly.\n"
                    error_msg +=  "ERROR: If you still have issues, please use gen_edgerc.py to generate the credentials\n"
                    error_msg +=  "ERROR: Problem details: %s\n" % result
                    exit(error_msg)
      
      if status_code in [404]:
                    error_msg =  "ERROR: Call to %s failed with a %s result\n" % (endpoint, status_code)
                    error_msg +=  "ERROR: This means that the page does not exist as requested.\n"
                    error_msg +=  "ERROR: Please ensure that the URL you're calling is correctly formatted\n"
                    error_msg +=  "ERROR: or look at other examples to make sure yours matches.\n"
                    error_msg +=  "ERROR: Problem details: %s\n" % details
                    exit(error_msg)
      
      error_string = None
      if "errorString" in result:
                   if result["errorString"]:
                           error_string = result["errorString"]
      else:
        for key in result:
          if type(key) is not str or isinstance(result, dict) or not isinstance(result[key], dict):
            continue
          if "errorString" in result[key] and type(result[key]["errorString"]) is str:
            error_string = result[key]["errorString"]
      if error_string:
                    error_msg =  "ERROR: Call caused a server fault.\n"
                    error_msg +=  "ERROR: Please check the problem details for more information:\n"
                    error_msg +=  "ERROR: Problem details: %s\n" % error_string
                    exit(error_msg)
    
    def postResult(self, endpoint, body, parameters=None):
        headers = {'content-type': 'application/json'}
        path = endpoint
        endpoint_result = self.session.post(parse.urljoin(self.baseurl,path), data=body, headers=headers, params=parameters)
        status = endpoint_result.status_code
        if self.verbose: print ("LOG: POST %s %s %s" % (path,status,endpoint_result.headers["content-type"]))
        if status == 204:
           return {}
        self.httpErrors(endpoint_result.status_code, path, endpoint_result.json())
        
        if self.verbose: print (">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n")
        return endpoint_result.json()

    def postFiles(self, endpoint, file):
        path = endpoint
        endpoint_result = self.session.post(parse.urljoin(self.baseurl,path), files=file)
        status = endpoint_result.status_code
        if self.verbose: print ("LOG: POST FILES %s %s %s" % (path,status,endpoint_result.headers["content-type"]))
        if status == 204:
           return {}
        self.httpErrors(endpoint_result.status_code, path, endpoint_result.json())
        
        if self.verbose: print (">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n")
        return endpoint_result.json()
    
    def putResult(self, endpoint, body, parameters=None):
        headers = {'content-type': 'application/json'}
        path = endpoint
        
        endpoint_result = self.session.put(parse.urljoin(self.baseurl,path), data=body, headers=headers, params=parameters)
        status = endpoint_result.status_code
        if self.verbose: print ("LOG: PUT %s %s %s" % (endpoint,status,endpoint_result.headers["content-type"]))
        if status == 204:
            return {}
        if self.verbose: print (">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n")
        return endpoint_result.json()
    
    def deleteResult(self, endpoint):
        endpoint_result = self.session.delete(parse.urljoin(self.baseurl,endpoint))
        status = endpoint_result.status_code
        if self.verbose: print ("LOG: DELETE %s %s %s" % (endpoint,status,endpoint_result.headers["content-type"]))
        if status == 204:
            return {}
        if self.verbose: print (">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n")
        return endpoint_result.json()
if sys.version_info[0] >= 3:
     # python3
     from urllib import parse
else:
     # python2.7
     import urlparse as parse

# Establish an HTTP session
session = requests.Session()

# Load the .edgerc credentials file
section_name = "default"
config = EdgeGridConfig({},section_name)

# Set up verbose output and debugging
if hasattr(config, "debug") and config.debug:
  debug = True
else:
	debug = False

if hasattr(config, "verbose") and config.verbose:
  verbose = True
else:
	verbose = False

# Set the EdgeGrid credentials
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

# If include any special headers (used for debugging)
if hasattr(config, 'headers'):
  session.headers.update(config.headers)

# Set up the base URL
baseurl = '%s://%s/' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(session, debug, verbose, baseurl)

# main code
if __name__ == "__main__":
	# Request the entitlement scope for the credentials
	credential_scope = httpCaller.getResult('/-/client-api/active-grants/implicit')

	if verbose: print (json.dumps(credential_scope, indent=2))

	print ("Credential Name: %s" % credential_scope['name'])
	print ("---")
	print ("Created: %s by %s" % (credential_scope['created'], credential_scope['createdBy']))
	print ("Updated: %s by %s" % (credential_scope['updated'], credential_scope['updatedBy']))
	print ("Activated: %s by %s" % (credential_scope['activated'], credential_scope['activatedBy']))
	print ("---")

	for scope in credential_scope['scope'].split(" "):
		o = parse.urlparse(scope)
		apis = o.path.split("/")
		print ('{0:35} {1:10}'.format(apis[3], apis[5]))

