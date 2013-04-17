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
""" plugins/renderers/db_directory_image.py - Basic Output for Any Folder """

import os
import os.path
from lxml import etree
from renderer_support import renderer_class


class db_directory_image(renderer_class):
    """ Default Folder Renderer - Basic Output for Any Folder """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/imgdir"
    _namespace_local = "imgdir"
    _default_content_mode = "title"
    _default_style_mode = "gallery"
    _default_recursion_depth = 1

    def getContent(self):
        if self._content_mode == "detailed" or self._content_mode == "summary" or self._content_mode == "title":
            if self._caller == "databrowse":
                uphref = self.getURLToParent(self._relpath)
                xmlroot = etree.Element('{%s}dir' % self._namespace_uri, path=self._fullpath, uphref=uphref, resurl=self._web_support.resurl, root="True")
                pass
            else:
                link = self.getURL(self._relpath)
                xmlroot = etree.Element('{%s}dir' % self._namespace_uri, name=os.path.basename(self._relpath), path=self._fullpath, href=link, resurl=self._web_support.resurl)
                pass
            if "ajax" in self._web_support.req.form:
                xmlroot.set("ajaxreq", "True")
                pass
            if self._recursion_depth is not 0:
                caller = 'db_directory_image'
                dirlist = self.getDirectoryList(self._fullpath)
                for item in dirlist:
                    itemrelpath = os.path.join(self._relpath, item)
                    itemfullpath = os.path.join(self._fullpath, item)
                    (handlers, icon) = self._handler_support.GetHandlerAndIcon(itemfullpath)
                    handler = handlers[-1]
                    if handler == "db_directory_image":
                        renderer = self.__class__(itemrelpath, itemfullpath, self._web_support, self._handler_support, caller, handlers, content_mode=self._content_mode, style_mode=self._style_mode, recursion_depth=self._recursion_depth-1)
                    else:
                        exec "import %s.%s as %s_module" % (handler, handler, handler)
                        exec "renderer = %s_module.%s(itemrelpath, itemfullpath, self._web_support, self._handler_support, caller, handlers, content_mode='%s', style_mode='%s', recursion_depth=%i)" % (handler, handler, self._content_mode, self._style_mode, self._recursion_depth - 1)
                    content = renderer.getContent()
                    xmlchild = etree.SubElement(xmlroot, '{%s}file' % (self._namespace_uri), fullpath=itemfullpath, relpath=itemrelpath, basename=os.path.basename(itemfullpath), link=self.getURL(itemrelpath), icon=icon)
                    if content is not None:
                        xmlchild.append(content)
                        pass
                    pass
                pass
            else:
                #ajax url and what not
                xmlroot.set("ajax", "True")
                xmlroot.set("ajaxurl", self.getURL(self._relpath, recursion_depth=1, nopagestyle=True, content_mode=self._content_mode, style_mode=self._style_mode))
                pass
            return xmlroot
        else:
            raise self.RendererException("Invalid Content Mode")
        pass

pass
