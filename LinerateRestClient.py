#!/usr/bin/env python

import json
import requests
import logging
import sys

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

REST_PATH = '/lrs/api/v1.0'
SSL_VERIFY = False
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'changeme'
OK_CODES_GET =    [ 200 ]
OK_CODES_PUT =    [ 200 ]
OK_CODES_DELETE = [ 204 ]
OK_CODES_LOGIN =  [ 200, 302 ]

class RestError(Exception):
    pass

class RestNode(object):
    def __init__(self, path, data):
        if not path.startswith('/'):
            path = '/' + path

        self.path = path
        self.parsed_json = json.loads(data)
        self.node_data = self.parsed_json[path]

    @property
    def type(self):
        return self.node_data['type']

    @property
    def is_default(self):
        return self.node_data['default']

    @property
    def data(self):
        return self.node_data['data']

    @property
    def can_delete(self):
        return self.node_data['deleteAllowed']

    def __str__(self):
        return self.data

    def __repr__(self):
        return json.dumps(self.parsed_json)

class Connection(object):

    def __init__(self,
                 hostname,
                 user=DEFAULT_USERNAME,
                 password=DEFAULT_PASSWORD,
                 port=8443,
                 timeout=5):

        self.hostname = hostname
        self.port = int(port)
        self.timeout = int(timeout)
        self.rest_path = REST_PATH
        self.ssl_verify = SSL_VERIFY
        self.base_url = 'https://%s:%i' % (self.hostname, self.port)
        self.rest_url = '%s%s' % (self.base_url, self.rest_path)

        # define return codes that signify success for each method
        self.ok_codes = {}
        self.ok_codes['get'] = OK_CODES_GET
        self.ok_codes['put'] = OK_CODES_PUT
        self.ok_codes['delete'] = OK_CODES_DELETE
        self.ok_codes['login'] = OK_CODES_LOGIN

        self.session = requests.Session()

        # default headers
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

        self._login(user,password)

    def _login(self, user, password):
        url = 'https://%s:%i/login' % (self.hostname, self.port)
        logger.debug('Connecting to %s' % (url))
        path = self.base_url + '/login'
        payload = json.dumps({'username': user, 'password': password})
        try:
            r = self.session.post(path,
                                 data=payload,
                                 verify=self.ssl_verify, 
                                 timeout=self.timeout)
        except requests.exceptions.Timeout:
            logger.error('Connection timed out')
            logger.debug(sys.exc_info())
            sys.exit()
        except requests.exceptions.ConnectionError:
            logger.error('Could not connect to target system %s:%i' % (self.hostname, self.port))
            logger.debug(sys.exc_info())
            sys.exit()
        except:
            logger.error('Unknown connection error')
            logger.error(sys.exc_info())
            sys.exit()
        else:
            if self.check_response(r, self.ok_codes['login']):
                self.sid_cookie = {'connect.sid': r.cookies['connect.sid']}


    def get(self, node):
        path = self.rest_url + node
        try:
            r = self.session.get(path,
                                 cookies=self.sid_cookie,
                                 verify=self.ssl_verify, 
                                 timeout=self.timeout)
            #print r.text
        except:
            print sys.exc_info()
        else:
            if self.check_response(r, self.ok_codes['get']):
                return RestNode(node, r.text)

    def put(self, node, data, data_type='string', default=False):
        path = self.rest_url + node
        payload = json.dumps({
                            'data': data, 
                            'type': data_type, 
                            'default': default})
        print payload
        try:
            r = self.session.put(path,
                                 data=payload,
                                 cookies=self.sid_cookie,
                                 verify=self.ssl_verify, 
                                 timeout=self.timeout)
        except:
            print sys.exc_info()
        else:
            if self.check_response(r, self.ok_codes['put']):
                return True



    def delete(self, node):
        path = self.rest_url + node
        # DELETE returns 500 unless a payload exists (bug?)
        payload = json.dumps({})
        try:
            r = self.session.delete(path,
                                 data = payload,
                                 cookies=self.sid_cookie,
                                 verify=self.ssl_verify, 
                                 timeout=self.timeout)
        except:
            print sys.exc_info()
        else:
            if self.check_response(r, self.ok_codes['delete']):
                return True

    def check_response(self, r, ok_codes):
        if r.status_code in ok_codes:
            return True
        else:
            raise RestError(r.status_code, r.text, r)


    def write_mem(self):
        self.put('/exec/system/util/copy', 'running-config|startup-config')



if __name__ == "__main__":
    pass
