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
""" plugins/renderers/db_checklist_viewer.py - Generic Checklist Files """

import os
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_checklist_viewer(renderer_class):
    """ Generic Checklist Files """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/checklist_chf"
    _namespace_local = "chf"
    _default_content_mode = "full"
    _default_style_mode = "view_filled_checklist"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode == "full":
                f = open(self._fullpath, 'r')
                xml = etree.parse(f)
                f.close()
                g = open(os.path.join(self._web_support.qautils, 'checklist/chf2html.xsl'), 'r')
                xsltransform = etree.parse(g)
                g.close()
                transformedxml = xml.xslt(xsltransform,rawlink_postfix="'?content_mode=raw'")
                xmloutput = etree.XML(str(transformedxml))
                return xmloutput
            else:
                raise self.RendererException("Invalid Content Mode")

    pass
