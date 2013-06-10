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
""" plugins/handlers/dbh_multimedia_directory.py - Image Directory Handler """

import os


def dbh_directory_image(path, contenttype, extension):
    """ Generic Image Directory Handler - Returns directory_image for all directories with more than 50 percent images """
    if contenttype.startswith("inode/directory") or contenttype.startswith("application/x-directory") or contenttype.startswith("directory"):
        dirlist = os.listdir(path)
        count = 0
        for item in dirlist:
            if (os.path.splitext(item)[1].lower() in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".avi", ".mpg", ".mpeg", ".mpe", ".mpeg-1", ".mpeg-2", ".m1s", ".mpa", ".mp2", ".m2a", ".mp2v", ".m2v", ".m2s", ".mov", ".qt", ".asf", ".asx", ".wmv", ".wma", ".wmx", ".rm", ".ra", ".ram", ".rmvb", ".mp4", ".3gp", ".ogm", ".mkv", ".sldprt", ".sldasm", ".slddrw", ".pmd"]):
                count = count + 1
        if count > (len(dirlist) * 0.5):
            return "db_multimedia_directory"
        else:
            return False
    else:
        return False
