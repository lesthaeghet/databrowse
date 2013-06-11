#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2013 Iowa State University                             ##
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
""" databrowse.wsgi - Entry Point for Main Application """

import sys
import os
import string
from lxml import etree

# Enable cgitb to provide better error message output
import cgitb
cgitb.enable()

serverwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:html="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="no" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:variable name="resdir">%s</xsl:variable>
    <xsl:template match="/">
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse">
            <body>
                <xsl:attribute name="db:resdir"><xsl:value-of select="$resdir"/></xsl:attribute>
                %s
                <xsl:apply-templates mode="%s"/>
            </body>
        </html>
    </xsl:template>
    %s
</xsl:stylesheet>'''

localwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:html="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="no" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:variable name="resdir">%s</xsl:variable>
    <xsl:template match="/">
        <xsl:processing-instruction name="xml-stylesheet">type="text/xsl" href="/dbres/db_web.xml"</xsl:processing-instruction>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse">
            <body>
                <xsl:attribute name="db:resdir"><xsl:value-of select="$resdir"/></xsl:attribute>
                %s
                <xsl:apply-templates mode="%s"/>
            </body>
        </html>
    </xsl:template>
    %s
</xsl:stylesheet>'''

ajaxwrapper = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" version="1.0">
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes" version="1.0" media-type="application/xhtml+xml" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>
    <xsl:template match="/">
        <xsl:apply-templates mode="%s"/>
    </xsl:template>
    %s
</xsl:stylesheet>'''


class FileResolver(etree.Resolver):
    _path = None

    def __init__(self, path):
        self._path = path
        pass

    def resolve(self, url, pubid, context):
        return self.resolve_filename(os.path.abspath(self._path + '/' + url), context)

    pass


def application(environ, start_response):
    """ Entry Point for WSGI Application """
    os.environ["HOME"] = "/home/www/.home"
    try:
        # Add paths and import support modules
        if os.path.dirname(environ['SCRIPT_FILENAME']) not in sys.path:
            sys.path.append(os.path.dirname(environ['SCRIPT_FILENAME']))
        if os.path.dirname(environ['SCRIPT_FILENAME'] + '/support/') not in sys.path:
            sys.path.append(os.path.dirname(environ['SCRIPT_FILENAME']) + '/support/')
        import web_support as db_web_support_module

        # Set up web_support class with environment information
        db_web_support = db_web_support_module.web_support(environ, start_response)

        # Determine Requested File/Folder Absolute Path and Path Relative to Dataroot
        if "path" not in db_web_support.req.form:
            fullpath = db_web_support.dataroot
            relpath = '/'
            pass
        else:
            fullpath = os.path.abspath(db_web_support.dataroot + '/' + db_web_support.req.form["path"].value)
            if not fullpath.startswith(db_web_support.dataroot):
                return db_web_support.req.return_error(403)
            if os.access(fullpath, os.R_OK) and os.path.exists(fullpath):
                if fullpath == db_web_support.dataroot:
                    relpath = '/'
                    pass
                else:
                    relpath = fullpath.replace(db_web_support.dataroot, '')
                    pass
                pass
            elif not os.path.exists(fullpath):
                return db_web_support.req.return_error(404)
            else:
                return db_web_support.req.return_error(401)
            pass

        # Import Plugin Directory
        if db_web_support.pluginpath not in sys.path:
            sys.path.append(db_web_support.pluginpath)

        # Determine handler for requested path
        import handler_support as handler_support_module
        handler_support = handler_support_module.handler_support(db_web_support.pluginpath, db_web_support.icondbpath, db_web_support.hiddenfiledbpath, db_web_support.directorypluginpath)
        handlers = handler_support.GetHandler(fullpath)
        handler = handlers[-1]

        # Let's see if we want to override the default handler
        if "handler" in db_web_support.req.form:
            handler = db_web_support.req.form['handler'].value
            pass

        # Get A Handle to The Rendering Plugin
        caller = "databrowse"
        exec "import %s.%s as %s_module" % (handler, handler, handler)
        exec "renderer = %s_module.%s(relpath, fullpath, db_web_support, handler_support, caller, handlers%s%s%s)" % (handler, handler,\
                    ', content_mode="' + db_web_support.req.form["content_mode"].value + '"' if "content_mode" in db_web_support.req.form else '',\
                    ', style_mode="' + db_web_support.req.form['style_mode'].value + '"' if "style_mode" in db_web_support.req.form else '',\
                    ', recursion_depth=' + db_web_support.req.form['recursion_depth'].value + '' if "recursion_depth" in db_web_support.req.form else '')

        # Register Primary Namespace
        etree.register_namespace('db', 'http://thermal.cnde.iastate.edu/databrowse')

        if not renderer.isRaw():
            # Prepare Top Menu String
            topbarstring = '<div class="pathbar">'
            linkstring = db_web_support.siteurl
            itemslist = string.split(relpath, "/")[1:]
            count = 1
            if itemslist[0] is not "":
                topbarstring += '<a style="padding:0 5px;position:relative;top:3px;" href="%s"><img src="%s/icons/go-home.png"/></a><a class="button" href="%s">/</a>&gt;' % (linkstring, db_web_support.resurl, linkstring)
                pass
            for item in itemslist:
                if item is not "" and count is not len(itemslist):
                    linkstring += "/" + item
                    topbarstring += '<a class="button" href="%s">%s</a>&gt;' % (linkstring, item)
                    pass
                elif item is not "" and count is len(itemslist):
                    linkstring += "/" + item
                    topbarstring += '<a class="button active" href="%s">%s</a>' % (linkstring, item)
                    pass
                else:
                    topbarstring += '<a style="padding:0 5px;position:relative;top:3px;" href="%s"><img src="%s/icons/go-home.png"/></a><a class="button active" href="%s">/</a>' % (linkstring, db_web_support.resurl, linkstring)
                    pass
                count += 1
                pass
            topbarstring += "</div>"

            # If we are only requesting content or style, output them
            if "contentonly" in db_web_support.req.form:
                xml = etree.ElementTree(renderer.getContent())
                db_web_support.req.response_headers['Content-Type'] = 'text/xml'
                db_web_support.req.output = etree.tostring(xml)
                return [db_web_support.req.return_page()]
            elif "styleonly" in db_web_support.req.form:
                style = serverwrapper % (db_web_support.resurl, topbarstring, renderer.getContentMode(), db_web_support.style.GetStyle())
                db_web_support.req.response_headers['Content-Type'] = 'text/xml'
                db_web_support.req.output = style
                return [db_web_support.req.return_page()]
            else:
                pass

            # If we want styling to be done by the browser or we don't want page styling
            parser = etree.XMLParser()
            parser.resolvers.add(FileResolver(os.path.dirname(fullpath)))
            if "ajax" in db_web_support.req.form:
                return renderer.getContent()
            elif renderer.getContentMode() is "ajax":
                xml = etree.ElementTree(renderer.getContent())
                style = ajaxwrapper % (renderer.getContentMode(), db_web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                db_web_support.req.output = etree.tostring(content)
                db_web_support.req.response_headers['Content-Type'] = 'application/xhtml+xml'
                return [db_web_support.req.return_page()]
            elif "nopagestyle" in db_web_support.req.form:
                xml = etree.ElementTree(renderer.getContent())
                style = serverwrapper % (db_web_support.resurl, topbarstring, renderer.getContentMode(), db_web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                db_web_support.req.output = etree.tostring(content)
                db_web_support.req.response_headers['Content-Type'] = 'application/xhtml+xml'
                return [db_web_support.req.return_page()]
            elif "localpagestyle" in db_web_support.req.form:
                xml = etree.ElementTree(renderer.getContent())
                style = localwrapper % (db_web_support.resurl, topbarstring, renderer.getContentMode(), db_web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                contentroot = content.getroot()
                renderer.loadMenu()
                contentroot.append(db_web_support.menu.GetMenu())
                db_web_support.req.output = etree.tostring(content)
                db_web_support.req.response_headers['Content-Type'] = 'application/xhtml+xml'
                return [db_web_support.req.return_page()]
            else:
                xml = etree.ElementTree(renderer.getContent())
                style = serverwrapper % (db_web_support.resurl, topbarstring, renderer.getContentMode(), db_web_support.style.GetStyle())
                content = xml.xslt(etree.XML(style, parser))
                contentroot = content.getroot()
                renderer.loadMenu()
                contentroot.append(db_web_support.menu.GetMenu())
                f = open(os.path.join(db_web_support.webdir, "resources/db_web.xml"))
                template = etree.parse(f)
                f.close()
                db_web_support.req.output = str(content.xslt(template))
                db_web_support.req.response_headers['Content-Type'] = 'application/xhtml+xml'
                #raise Exception("Testing")
                return [db_web_support.req.return_page()]
        else:
            # We're outputting raw content, so pass it off to the plugin to do its thing
            return renderer.getContent()
        pass
    except Exception as err:
        # Something has gone terribly wrong, let's display some useful information to the user
        # Error Page Template
        errormessage = '''\
<?xml-stylesheet type="text/xsl" href="/dbres/db_web.xml"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:html="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse">
<body db:resdir="/dbres/">
    <h1>500 Internal Server Error</h1>
    <p>An unhandled exception has occurred.  Notify the administrators for assistance.  Please make note of what you were doing, the steps to reproduce the error, and the approximate time.  More details are shown below:</p>
    <p>
        <strong>Error:</strong>  %s                                                     <br/>
        <strong>Time:</strong> %s                                                       <br/>
        <strong>Hostname:</strong> %s                                                   <br/>
        <strong>Platform:</strong> %s <strong>Python:</strong> %s                       <br/>
        <strong>PID:</strong> %s <strong>UID:</strong> %s <strong>GID:</strong> %s      <br/>
        <strong>Traceback:</strong>                                                     <br/>
        <pre style="overflow:auto">%s</pre>
        <strong>Environment:</strong>                                                   <br/>
        <pre style="overflow:auto">%s</pre>
        <strong>Request Variables:</strong>                                             <br/>
        <pre style="overflow:auto">%s</pre>
        <strong>Dir()</strong>                                                          <br/>
        <pre style="overflow:auto">%s</pre>
    </p>
</body>
<db:navigation xmlns="http://www.w3.org/1999/xhtml" xmlns:db="http://thermal.cnde.iastate.edu/databrowse">
    <db:navbar>
        <db:navelem><a href="javascript:window.history.back()">Go Back</a></db:navelem>
    </db:navbar>
</db:navigation>
</html>'''

        # Import Modules Needed For All Of This - No need to import these things otherwise
        import traceback
        import StringIO
        import cgi
        import socket
        from time import gmtime, strftime

        # Get Our Own FieldStorage Object
        fs = environ['wsgi.input'] if isinstance(environ['wsgi.input'], cgi.FieldStorage) else None
        if fs is None:
            form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ, keep_blank_values=1)
            pass
        else:
            form = fs
            pass

        # Get a Trace and Also Output a Copy of the Trace to the Server Log
        trace = StringIO.StringIO()
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=trace)
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        tracestring = trace.getvalue()
        trace.close()
        tracestring = tracestring.replace('&', "&#160;").replace('<', "&lt;").replace('>', "&gt;")

        # Return Proper Error so AJAX Works
        if "ajax" in form:
            start_response('500 Internal Server Error', {'Content-Type': 'text/html', 'Content-Length': '25'})
            return ['500 Internal Server Error']
        else:
            # Now we can get a list of request variables
            inputstring = ""
            for key in form.keys():
                inputstring = inputstring + "%s:  %s \n" % (key, repr(form[key].value))
                pass
            inputstring = inputstring.replace('<', "&lt;").replace('>', "&gt;").replace('&', "&#160;")

            # Get A List of Everything in Environ
            keystring = ""
            keys = environ.keys()
            keys.sort()
            for key in keys:
                keystring = keystring + "%s:  %s \n" % (key, repr(environ[key]))
                pass
            keystring = keystring.replace('&', "&#160;").replace('<', "&lt;").replace('>', "&gt;")

            # Get a list of everything in dir()
            dirstring = ""
            for name in dir():
                dirstring = dirstring + "%s %s: %s \n" % (name, str(type(name)), repr(eval(name)))
            dirstring = dirstring.replace('&', "&#160;").replace('<', "&lt;").replace('>', "&gt;")

            # Output Error Message
            errormessage = errormessage % (err, strftime("%Y-%m-%d %H:%M:%S", gmtime()), socket.getfqdn(), sys.platform, sys.version, os.getpid(), os.getuid(), os.getgid(), tracestring, keystring, inputstring, dirstring)
            start_response('200 OK', {'Content-Type': 'text/xml', 'Content-Length': str(len(errormessage))}.items())
            return [errormessage]
        pass


class Debugger:
    """ Code Used To Enable PDB in Single Instance Apache Mode """

    def __init__(self, object):
        self.__object = object

    def __call__(self, *args, **kwargs):
        import pdb
        import sys
        debugger = pdb.Pdb()
        debugger.use_rawinput = 0
        debugger.reset()
        sys.settrace(debugger.trace_dispatch)

        try:
            return self.__object(*args, **kwargs)
        finally:
            debugger.quitting = 1
            sys.settrace(None)
        pass
    pass

# Uncomment this line to enable PDB
# Apache must be ran in single instance mode using the following commands:
#   sudo /etc/init.d/httpd stop
#   httpd -X
#application = Debugger(application)
