#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012 Iowa State University                                  ##
##                                                                           ##
## This program is free software: you can redistribute it and/or modify      ##
## it under the terms of the GNU General Public License as published by      ##
## the Free Software Foundation, either version 3 of the License, or         ##
## (at your option) any later version.                                       ##
##                                                                           ##
## This program is distributed in the hope that it will be useful,           ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of            ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             ##
## GNU General Public License for more details.                              ##
##                                                                           ##
## You should have received a copy of the GNU General Public License         ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>.     ##
###############################################################################
""" support/web_support.py - Classes to encapsulate Web/WSGI functionality """

import os
import os.path
import cgi


class wsgi_req:
    """ A simple wrapper for the wsgi request """

    environ = None              # environment dictionary
    start_response = None       # start_response function to call before finalization
    filename = None             # name of script that was called
    dirname = None              # name of directory containing script that was called
    unparsed_uri = None         # request URI
    form = None                 # form parameters
    status = None               # Status string
    output = None               # Output string
    response_headers = None     # Dictionary of response headers
    output_done = None          # Flag: Have we generated output yet or not?

    def __init__(self, environ, start_response):
        """ Load Values from Request """
        self.environ = environ
        self.start_response = start_response
        self.filename = environ['SCRIPT_FILENAME']
        self.dirname = os.path.dirname(self.filename)
        self.unparse_uri = environ['REQUEST_URI']
        self.form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ, keep_blank_values=1)

        self.status = '200 OK'
        self.response_headers = {}
        self.response_headers['Content-Type'] = 'text/xml'
        self.output_done = False

        if "debug" in self.form:
            self.response_headers["Content-Type"] = "text/plain"    # can switch to "text/plain" for debugging -- add ?debug to end of URL
            # config.req.output=str(config.req.form)+str(config.req.form["debug"])
            pass

        pass

    def return_page(self):
        """ Send Webpage Output """
        self.response_headers['Content-Length'] = str(len(self.output))
        self.start_response(self.status, self.response_headers.items())
        self.output_done = True
        return [self.output.encode('utf-8')]

    def return_error(self, status=500):
        """ Return Error Message """
        if status == 400:
            self.status = '400 Bad Request'
        elif status == 401:
            self.status = '401 Unauthorized'
        elif status == 403:
            self.status = '403 Forbidden'
        elif status == 404:
            self.status = '404 Page Not Found'
        elif status == 405:
            self.status = '405 Method Not Allowed'
        elif status == 406:
            self.status = '406 Not Acceptable'
        elif status == 500:
            self.status = '500 Internal Server Error'
        elif status == 501:
            self.status = '501 Not Implemented'
        elif status == 503:
            self.status = '503 Service Unavailable'
        else:
            self.status = '500 Internal Server Error'

        self.output_done = True
        self.response_headers = {}
        self.response_headers['Content-Type'] = 'text/html'
        self.response_headers['Content-Length'] = str(len(self.status.encode('utf-8')))
        self.start_response(self.status, self.response_headers.items())
        return [self.status.encode('utf-8')]

    pass


class web_support:
    """ Class containing support functionality for web operations """
    req = None                  # request class object
    req_filename = None         # requested filename
    req_dir = None              # directory containing the requested file
    confstr = None              # string containing optional configuration file
    email_sendmail = None       # email:  sendmail location
    email_admin = None          # email:  admin email for alert reports, etc
    email_from = None           # email:  email address mail should appear from
    administrators = None       # dictionary containing administrator list
    sitetitle = None            # site title
    shorttitle = None           # abbreviated site title

    def __init__(self, environ, start_response):
        self.req = wsgi_req(environ, start_response)
        self.reqfilename = self.req.filename
        self.webdir = os.path.dirname(self.reqfilename)

        # Try to Load Optional Configuration File
        try:
            conffile = file(os.path.join(os.path.dirname(self.reqfilename), "web.conf"))
            self.confstr = conffile.read()
            conffile.close()
            exec self.confstr
        except:
            pass

        # Set Default Configuration Options
        if self.email_sendmail is None:
            self.email_sendmail = "/usr/lib/sendmail -i"
            pass

        if self.email_admin is None:
            self.email_admin = "tylerl@iastate.edu"
            pass

        if self.email_from is None:
            self.emailfrom = "tylerl@iastate.edu"
            pass

        if self.administrators is None:
            self.administrators = {"sdh4": "Steve Holland", "tylerl": "Tyler Lesthaeghe"}
            pass

        if self.sitetitle is None:
            self.sitetitle = "Databrowse Project Browser"
            pass

        if self.shorttitle is None:
            self.shorttitle = "databrowse"
            pass

        pass

    pass
