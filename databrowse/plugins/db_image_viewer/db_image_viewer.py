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
""" plugins/renderers/db_image_generic.py - Default Image Renderer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import magic
import Image
import StringIO
import databrowse.support.EXIF as EXIF
import databrowse.support.RMETA as RMETA


class db_image_viewer(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/image"
    _namespace_local = "image"
    _default_content_mode = "full"
    _default_style_mode = "view_image"
    _default_recursion_depth = 2

    def getContent(self):
        if self._content_mode == "full":
            try:
                st = os.stat(self._fullpath)
            except IOError:
                return "Failed To Get File Information: %s" % (self._fullpath)
            else:
                file_size = st[ST_SIZE]
                file_mtime = time.asctime(time.localtime(st[ST_MTIME]))
                file_ctime = time.asctime(time.localtime(st[ST_CTIME]))
                file_atime = time.asctime(time.localtime(st[ST_ATIME]))

                src = self.getURL(self._relpath, content_mode="raw", thumbnail="medium")
                href = self.getURL(self._relpath, content_mode="raw")
                downlink = self.getURL(self._relpath, content_mode="raw", download="true")

                xmlroot = etree.Element('{%s}image' % self._namespace_uri, name=os.path.basename(self._relpath), src=src, href=href, resurl=self._web_support.resurl, downlink=downlink)

                xmlchild = etree.SubElement(xmlroot, "filename")
                xmlchild.text = os.path.basename(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "path")
                xmlchild.text = os.path.dirname(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "filesize")
                xmlchild.text = self.ConvertUserFriendlySize(file_size)

                xmlchild = etree.SubElement(xmlroot, "mtime")
                xmlchild.text = file_mtime

                xmlchild = etree.SubElement(xmlroot, "ctime")
                xmlchild.text = file_ctime

                xmlchild = etree.SubElement(xmlroot, "atime")
                xmlchild.text = file_atime

                # File Permissions
                xmlchild = etree.SubElement(xmlroot, "permissions")
                xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                # User and Group
                username = pwd.getpwuid(st[ST_UID])[0]
                groupname = grp.getgrgid(st[ST_GID])[0]
                xmlchild = etree.SubElement(xmlroot, "owner")
                xmlchild.text = "%s:%s" % (username, groupname)

                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                xmlchild = etree.SubElement(xmlroot, "contenttype")
                xmlchild.text = contenttype

                img = Image.open(self._fullpath)
                xmlchild = etree.SubElement(xmlroot, "imgsize")
                xmlchild.text = "%s x %s pixels" % img.size
                xmlchild = etree.SubElement(xmlroot, "imgmode")
                xmlchild.text = img.mode

                pmdfile = os.path.splitext(self._fullpath)[0]+'.pmd'
                if os.access(pmdfile, os.R_OK) and os.path.exists(pmdfile):
                    f = open(pmdfile, 'r')
                    pmddoc = etree.parse(f)
                    f.close()
                    pmdroot = pmddoc.getroot()
                    xmlroot.append(pmdroot)
                    pass

                f = open(self._fullpath, 'rb')
                exiftags = EXIF.process_file(f)
                f.seek(0)
                ricohtags = RMETA.process_file(f)
                f.close()

                xmlchild = etree.SubElement(xmlroot, "exiftags")
                x = exiftags.keys()
                x.sort()
                for tag in x:
                    if tag in ('JPEGThumbnail', 'TIFFThumbnail'):
                        continue
                    newxmltag = etree.SubElement(xmlchild, "tag", name=tag)
                    newxmltag.text = repr(exiftags[tag].printable)
                    pass

                xmlchild = etree.SubElement(xmlroot, "ricohtags")
                for tag in ricohtags:
                    newxmltag = etree.SubElement(xmlchild, "tag", name=str(tag))
                    newxmltag.text = repr(ricohtags[tag])
                    pass

                return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            link = self.getURL(self._relpath)
            src = self.getURL(self._relpath, content_mode="raw", thumbnail="gallery")
            href = self.getURL(self._relpath, content_mode="raw")
            downlink = self.getURL(self._relpath, content_mode="raw", download="true")
            xmlroot = etree.Element('{%s}image' % self._namespace_uri, name=os.path.basename(self._relpath), link=link, src=src, href=href, downlink=downlink)
            return xmlroot
        elif self._content_mode == "raw":
            magicstore = magic.open(magic.MAGIC_MIME)
            magicstore.load()
            contenttype = magicstore.file(self._fullpath)
            if "thumbnail" in self._web_support.req.form:
                if self._web_support.req.form['thumbnail'].value == "small":
                    tagname = "small"
                    newsize = (150, 150)
                elif self._web_support.req.form['thumbnail'].value == "medium":
                    tagname = "medium"
                    newsize = (300, 300)
                elif self._web_support.req.form['thumbnail'].value == "large":
                    tagname = "large"
                    newsize = (500, 500)
                elif self._web_support.req.form['thumbnail'].value == "gallery":
                    tagname = "gallery"
                    newsize = (201, 201)
                else:
                    tagname = "small"
                    newsize = (150, 150)
                if self.CacheFileExists(tagname):
                    size = os.path.getsize(self.getCacheFileName(tagname))
                    f = self.getCacheFileHandler('rb', tagname)
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    img = Image.open(self._fullpath)
                    format = img.format
                    img.thumbnail(newsize, Image.ANTIALIAS)
                    output = StringIO.StringIO()
                    img.save(output, format=format)
                    f = self.getCacheFileHandler('wb', tagname)
                    img.save(f, format=format)
                    f.close()
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    return [output.getvalue()]
            else:
                size = os.path.getsize(self._fullpath)
                f = open(self._fullpath, "rb")
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                if "download" in self._web_support.req.form:
                    self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024))
        else:
            raise self.RendererException("Invalid Content Mode")
        pass

    pass
