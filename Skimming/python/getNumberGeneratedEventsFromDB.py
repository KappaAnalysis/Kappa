#!/usr/bin/env python

import httplib
import urllib
import urllib2

# fix ca verification error in Python 2.7.9
try:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key=None, cert=None):
        urllib2.HTTPSHandler.__init__(self)
        self.key, self.cert = key, cert
    def https_open(self, req):
        return self.do_open(self.getConnection, req)
    def getConnection(self, host, timeout = None):
            return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

class RestClient(object):
    def __init__(self, cert=None, default_headers=None):
        self.cert = cert
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        if default_headers:
            self.headers = default_headers

    def _build_opener(self):
        if self.cert:
            cert_handler = HTTPSClientAuthHandler(self.cert, self.cert)
            return urllib2.build_opener(cert_handler)
        else:
            return urllib2.build_opener()

    def _format_url(self, url, api, params):
        if api:
            url += '/%s' % api

        if params:
            url += '?%s' % urllib.urlencode(params)

        return url

    def _request_headers(self, headers):
        request_headers = {}
        request_headers.update(self.headers)

        if headers:
            request_headers.update(headers)

        return request_headers

    def get(self, url, api=None, headers=None, params=None):
        request_headers = self._request_headers(headers)

        url = self._format_url(url, api, params)
        # print url
        opener = self._build_opener()
        return opener.open(urllib2.Request(url, None, request_headers)).read()

def getNumberGeneratedEventsFromDB(dataset, dbsinstance=None):
    url = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader'
    if dbsinstance:
	url = 'https://cmsweb.cern.ch/dbs/prod/'+dbsinstance+'/DBSReader'
 #   dataset ='/GluGluHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM'
    import os
    cert = os.environ['X509_USER_PROXY']
    if(cert==""):
      print "X509_USER_PROXY not properly set. Get a voms proxy and set this environment variable"
      sys.exit()
    rest_client = RestClient(cert=cert)
    import ast
    answer=ast.literal_eval(rest_client.get(url, api='blocksummaries', params={'dataset': dataset}))
    return str(answer[0]["num_event"])

def getNumberFilesFromDB(dataset, dbsinstance=None):
    url = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader'
    if dbsinstance:
	url = 'https://cmsweb.cern.ch/dbs/prod/'+dbsinstance+'/DBSReader'
 #   dataset ='/GluGluHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM'
    import os
    cert = os.environ['X509_USER_PROXY']
    if(cert==""):
      print "X509_USER_PROXY not properly set. Get a voms proxy and set this environment variable"
      sys.exit()
    rest_client = RestClient(cert=cert)
    import ast
    answer=ast.literal_eval(rest_client.get(url, api='blocksummaries', params={'dataset': dataset}))
    return str(answer[0]["num_file"])
