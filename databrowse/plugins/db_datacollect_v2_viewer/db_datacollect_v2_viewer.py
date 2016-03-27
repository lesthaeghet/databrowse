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
""" plugins/renderers/db_xlg_viewer.py - Experiment Log Viewer """

import sys
import os
import glob
import zipfile
import tempfile
from lxml import etree
from databrowse.support.renderer_support import renderer_class
from databrowse.plugins.db_data_table.db_data_table import db_data_table
import magic


class db_datacollect_v2_viewer(renderer_class):
    """ Experiment Log Viewer """

    _namespace_uri = "http://thermal.cnde.iastate.edu/datacollect"
    _namespace_local = "dc"
    _default_content_mode = "full"
    _default_style_mode = "log_view"
    _default_recursion_depth = 2

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode == "full" and self._style_mode in ['old_log_view','old_tabular_view']:
                # Contents of File
                #f = open(self._fullpath)
                #xmlroot = etree.XML(f.read())
                p = etree.XMLParser(huge_tree=True)
                xmlroot = etree.parse(self._fullpath, parser=p).getroot()
                # Resolve URL to Files Directory
                try:
                   reldest = xmlroot.xpath('dc:summary/dc:reldest', namespaces={'dc': 'http://thermal.cnde.iastate.edu/datacollect'})[0].text
                   reldesturl = self.getURL(os.path.abspath(os.path.join(os.path.dirname(self._relpath), reldest)))
                   xmlroot.set('reldesturl', reldesturl)
                except:
                   xmlroot.set('reldesturl', '')
                # Resolve URLs for Config Files
                configlist = xmlroot.xpath('dc:configstr', namespaces={'dc': 'http://thermal.cnde.iastate.edu/datacollect'})
                for item in configlist:
                    try:
                        fname = item.get('fname')
                        fnames = item.get('fnames')
                        if fname:
                            path = os.path.realpath(fname)
                            if path.startswith(self._web_support.dataroot) and os.access(path, os.R_OK) and os.path.exists(path):
                                relpath = path.replace(self._web_support.dataroot, '')
                                url = self.getURL(relpath)
                                item.set('url', url)
                        elif fnames:
                            if fnames[0] == '[' and fnames[-1] == "]":
                                urls = []
                                fnamelist = fnames[1:-1].split(',')
                                for fname in fnamelist:
                                    fname = fname.replace("'", "").replace('"', "").strip()
                                    path = os.path.realpath(fname)
                                    if path.startswith(self._web_support.dataroot) and os.access(path, os.R_OK) and os.path.exists(path):
                                        relpath = path.replace(self._web_support.dataroot, '')
                                        url = self.getURL(relpath)
                                        urls.append(url)
                                    else:
                                        urls.append("")
                                item.set('urls', repr(urls))
                    except:
                        pass
                # Resolve URLs for Specimen Database
                specimenlist = xmlroot.xpath('//dc:specimen', namespaces={"dc": 'http://thermal.cnde.iastate.edu/datacollect', "dcv": 'http://thermal.cnde.iastate.edu/dcvalue'})
                for item in specimenlist:
                    if item.text:
                        relpath = '/specimens/' + item.text + '.sdb'
                        if os.access(os.path.abspath(self._web_support.dataroot + "/" + relpath), os.R_OK) and os.path.exists(os.path.abspath(self._web_support.dataroot + "/" + relpath)):
                            url = self.getURL(relpath)
                            item.set('url', url)
                # Resolve URLs for Transducer Database
                transducerlist = xmlroot.xpath('//dc:xducer', namespaces={"dc": 'http://thermal.cnde.iastate.edu/datacollect', "dcv": 'http://thermal.cnde.iastate.edu/dcvalue'})
                for item in transducerlist:
                    if item.text:
                        relpath = '/transducers/' + item.text + '.tdb'
                        if os.access(os.path.abspath(self._web_support.dataroot + "/" + relpath), os.R_OK) and os.path.exists(os.path.abspath(self._web_support.dataroot + "/" + relpath)):
                            url = self.getURL(relpath)
                            item.set('url', url)
                return xmlroot
            elif self._content_mode == "full" and self._style_mode != 'dcv2_custom_view':
                # Contents of File
                #f = open(self._fullpath)
                #xmlroot = etree.XML(f.read())
                p = etree.XMLParser(huge_tree=True)
                xmlroot = etree.parse(self._fullpath, parser=p).getroot()
                
                # TODO:  GET RID OF ALL OF THIS BELOW
                # Resolve URLs for Config Files
                configlist = xmlroot.xpath('dc:config/dc:configfile', namespaces={'dc': 'http://thermal.cnde.iastate.edu/datacollect'})
                for item in configlist:
                    try:
                        xlink = item.get('{http://www.w3.org/1999/xlink}href')
                        if xlink:
                            path = os.path.realpath(fname)
                            if path.startswith(self._web_support.dataroot) and os.access(path, os.R_OK) and os.path.exists(path):
                                relpath = path.replace(self._web_support.dataroot, '')
                                url = self.getURL(relpath)
                                item.set('url', url)
                    except:
                        pass
                # Resolve URLs for Specimen Database
                specimenlist = xmlroot.xpath('//dc:specimen', namespaces={"dc": 'http://thermal.cnde.iastate.edu/datacollect', "dcv": 'http://thermal.cnde.iastate.edu/dcvalue'})
                for item in specimenlist:
                    if item.text:
                        relpath = '/specimens/' + item.text + '.sdb'
                        if os.access(os.path.abspath(self._web_support.dataroot + "/" + relpath), os.R_OK) and os.path.exists(os.path.abspath(self._web_support.dataroot + "/" + relpath)):
                            url = self.getURL(relpath)
                            item.set('url', url)
                # Resolve URLs for Transducer Database
                transducerlist = xmlroot.xpath('//dc:xducer', namespaces={"dc": 'http://thermal.cnde.iastate.edu/datacollect', "dcv": 'http://thermal.cnde.iastate.edu/dcvalue'})
                for item in transducerlist:
                    if item.text:
                        relpath = '/transducers/' + item.text + '.tdb'
                        if os.access(os.path.abspath(self._web_support.dataroot + "/" + relpath), os.R_OK) and os.path.exists(os.path.abspath(self._web_support.dataroot + "/" + relpath)):
                            url = self.getURL(relpath)
                            item.set('url', url)
                return xmlroot            
            elif self._content_mode == "full" and self._style_mode == "dcv2_custom_view":
                self._namespace_local = "dt"
                self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/datatable"
                if not 'custom_view' in self._web_support.req.form:
                    raise self.RendererException("Custom View Selection Required")
                    pass
                xml = etree.parse(os.path.join(os.path.dirname(self._fullpath), self._web_support.req.form['custom_view'].value))
                namespaces = " ".join(["xmlns:" + str(item) + '="' + str(value) + '"' for item, value in xml.getroot().nsmap.iteritems()])
                root = xml.getroot()
                root.set('filenamematch', os.path.basename(self._fullpath)) # Force it to only operate on this file
                ext_module = db_data_table.MyExt(os.path.join(os.path.dirname(self._fullpath), self._web_support.req.form['custom_view'].value))
                extensions = etree.Extension(ext_module, ('data', 'xmlassert'), ns='http://thermal.cnde.iastate.edu/databrowse/datatable/functions')
                root = xml.xslt(etree.XML(db_data_table._table_transform % (namespaces, self._web_support.siteurl, self.getURL(os.path.join(os.path.dirname(self._relpath), self._web_support.req.form['custom_view'].value)), self._web_support.req.form['custom_view'].value)), extensions=extensions).getroot()
                root.set('custom_view', self._web_support.req.form['custom_view'].value)
                return root
            elif self._content_mode == "raw":
                if 'filetype' in self._web_support.req.form:
                    self._namespace_local = "dt"
                    self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/datatable"
                    if not 'custom_view' in self._web_support.req.form:
                        raise self.RendererException("Custom View Selection Required")
                        pass
                    xml = etree.parse(os.path.join(os.path.dirname(self._fullpath), self._web_support.req.form['custom_view'].value))
                    namespaces = " ".join(["xmlns:" + str(item) + '="' + str(value) + '"' for item, value in xml.getroot().nsmap.iteritems()])
                    root = xml.getroot()
                    root.set('filenamematch', os.path.basename(self._fullpath)) # Force it to only operate on this file
                    ext_module = db_data_table.MyExt(os.path.join(os.path.dirname(self._fullpath), self._web_support.req.form['custom_view'].value))
                    extensions = etree.Extension(ext_module, ('data', 'xmlassert'), ns='http://thermal.cnde.iastate.edu/databrowse/datatable/functions')
                    base = xml.xslt(etree.XML(db_data_table._table_transform % (namespaces, self._web_support.siteurl, self.getURL(os.path.join(os.path.dirname(self._relpath), self._web_support.req.form['custom_view'].value)), self._web_support.req.form['custom_view'].value)), extensions=extensions)
                    filename = str(base.xpath('//@title')[0])
                    if self._web_support.req.form['filetype'].value == 'ods':
                        result = etree.tostring(base.xslt(etree.XML(db_data_table._ods_transform)))
                        
                        # File Creation
                        f = tempfile.TemporaryFile()
                        if sys.version_info[0] <= 2 and sys.version_info[1] < 7:
                            zipfile_compression=zipfile.ZIP_STORED
                            pass
                        else:
                            zipfile_compression=zipfile.ZIP_DEFLATED
                            pass
                        zf = zipfile.ZipFile(f,"w",zipfile_compression)
                        if sys.version_info[0] <= 2 and sys.version_info[1] < 7:
                            zf.writestr("mimetype","application/vnd.oasis.opendocument.spreadsheet");
                            pass
                        else:
                            # on Python 2.7 can explicitly specify lack of compression for this file alone 
                            zf.writestr("mimetype","application/vnd.oasis.opendocument.spreadsheet",compress_type=zipfile.ZIP_STORED)
                            pass
                        zf.writestr("META-INF/manifest.xml",r"""<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
    <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.spreadsheet" manifest:full-path="/"/>
    <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
    <!-- manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/-->
    <!-- manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/-->
    <!-- manifest:file-entry manifest:media-type="text/xml" manifest:full-path="settings.xml"/-->
</manifest:manifest>
""");

                        zf.writestr("content.xml",result)
                        zf.close()

                        # File Streaming
                        self._web_support.req.response_headers['Content-Type'] = 'application/vnd.oasis.opendocument.spreadsheet'
                        self._web_support.req.response_headers['Content-Length'] = str(f.tell())
                        f.seek(0, 0)
                        self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + filename + ".ods"
                        self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                        self._web_support.req.output_done = True
                        if 'wsgi.file_wrapper' in self._web_support.req.environ:
                            return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                        else:
                            return iter(lambda: f.read(1024))
                        pass
                    elif self._web_support.req.form['filetype'].value == 'csv':
                        # File Creation
                        f = tempfile.TemporaryFile()
                        coldef = base.xpath('dt:header/dt:coldef', namespaces={'dt':'http://thermal.cnde.iastate.edu/databrowse/datatable'})
                        f.write(",".join([x.text for x in coldef]) + '\n')
                        for row in base.xpath('dt:row', namespaces={'dt':'http://thermal.cnde.iastate.edu/databrowse/datatable'}):
                            datadef = row.xpath('dt:data/.', namespaces={'dt':'http://thermal.cnde.iastate.edu/databrowse/datatable'})
                            f.write(",".join([x.text if x.text is not None else '' for x in datadef]) + '\n')
                            pass
                        f.flush()
                        f.seek(0,2)

                        # File Streaming
                        self._web_support.req.response_headers['Content-Type'] = 'text/csv'
                        self._web_support.req.response_headers['Content-Length'] = str(f.tell())
                        f.seek(0, 0)
                        self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + filename + ".csv"
                        self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                        self._web_support.req.output_done = True
                        if 'wsgi.file_wrapper' in self._web_support.req.environ:
                            return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                        else:
                            return iter(lambda: f.read(1024))
                        pass
                    else:
                        raise self.RendererException('Invalid File Type')
                    pass
                else:
                    size = os.path.getsize(self._fullpath)
                    magicstore = magic.open(magic.MAGIC_MIME)
                    magicstore.load()
                    contenttype = magicstore.file(self._fullpath)
                    f = open(self._fullpath, "rb")
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.response_headers['Content-Length'] = str(size)
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

    def loadMenu(self):
        """ Load Menu Items for all current handlers """
        newmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar')
        isDirectory = os.path.isdir(self._fullpath)
        for handler in reversed(self._handlers):
            #Back to Copied Code
            dirlist = [os.path.splitext(item)[0][4:] for item in os.listdir(os.path.abspath(os.path.dirname(sys.modules['databrowse.plugins.' + handler].__file__) + '/')) if item.lower().startswith("dbs_")]
            additionalitems = []
            if isDirectory:
                if os.path.exists(os.path.join(self._fullpath, '.databrowse', 'stylesheets', handler)):
                    additionalitems = [os.path.splitext(item)[0][4:] for item in os.listdir(os.path.join(self._fullpath, '.databrowse', 'stylesheets', handler)) if item.lower().startswith("dbs_")]
            else:
                if os.path.exists(os.path.join(os.path.dirname(self._fullpath), '.databrowse', 'stylesheets', handler)):
                    additionalitems = [os.path.splitext(item)[0][4:] for item in os.listdir(os.path.join(os.path.dirname(self._fullpath), '.databrowse', 'stylesheets', handler)) if item.lower().startswith("dbs_")]
            dirlist = dirlist + additionalitems
            navelem = etree.SubElement(newmenu, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
            title = etree.SubElement(navelem, "{http://www.w3.org/1999/xhtml}a")
            title.text = " ".join([i[0].title()+i[1:] for i in handler[3:].split("_")])
            navitems = etree.SubElement(navelem, "{http://thermal.cnde.iastate.edu/databrowse}navdir", alwaysopen="true")
            for item in dirlist:
                if item not in self._handler_support.hiddenstylesheets:
                    if not isDirectory and item not in self._handler_support.directorystylesheets:
                        link = self.getURL(self._relpath, handler=handler, style_mode=item)
                        if self._style_mode == item and self.__class__.__name__ == handler:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem", selected="true")
                        else:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
                        menuitem = etree.SubElement(itemelem, "{http://www.w3.org/1999/xhtml}a", href=link)
                        menuitem.text = " ".join([i[0].title()+i[1:] for i in item.split("_")])
                        pass
                    elif isDirectory:
                        link = self.getURL(self._relpath, handler=handler, style_mode=item)
                        if self._style_mode == item and self.__class__.__name__ == handler:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem", selected="true")
                        else:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
                        menuitem = etree.SubElement(itemelem, "{http://www.w3.org/1999/xhtml}a", href=link)
                        menuitem.text = " ".join([i[0].title()+i[1:] for i in item.split("_")])
                        pass
                    else:
                        pass
                    pass
                pass
            pass
        # Get Parameters in Current Directory
        curdirlist = [item for item in os.listdir(os.path.abspath(os.path.dirname(self._fullpath))) if os.path.splitext(item)[1] == ".tbl"]
        customitems = {}
        cwd = os.getcwd()
        os.chdir(os.path.dirname(self._fullpath))
        for item in curdirlist:
            try:
                xml = etree.parse(os.path.abspath(os.path.join(os.path.dirname(self._fullpath), item)))
                filename = xml.xpath('@filenamematch')[0]                    
                filelist = glob.glob(filename)
                for filename in filelist:
                    if filename == os.path.basename(self._fullpath):
                        it = item if not item.startswith('.') else item[1:]
                        title = " ".join([i[0].title()+i[1:] for i in os.path.splitext(it)[0].split("_")])
                        customitems[item] = title
                        pass
                    pass                    
                pass
            except:
                pass
            pass
        os.chdir(cwd)
        navelem = newmenu[0]
        navitems = navelem[1]
        for item in customitems:
            link = self.getURL(self._relpath, handler='db_datacollect_v2_viewer', style_mode='dcv2_custom_view', custom_view=item)
            if self._style_mode == 'dcv2_custom_view' and self._web_support.req.form['custom_view'].value == item:
                itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem", selected="true")
            else:
                itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
            menuitem = etree.SubElement(itemelem, "{http://www.w3.org/1999/xhtml}a", href=link)
            menuitem.text = customitems[item]
            pass
        self._web_support.menu.AddMenu(newmenu)
        pass
