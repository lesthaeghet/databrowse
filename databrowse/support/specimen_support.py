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
""" support/specimen_support.py - Functions to Support Specimen Database """

import os
from lxml import etree

specimendb = '/databrowse/specimens'
NS = {"specimen": "http://thermal.cnde.iastate.edu/specimen"}
NSSTR = "{http://thermal.cnde.iastate.edu/specimen}"
OUTPUT_STRING = 0
OUTPUT_ELEMENT = 1
OUTPUT_ETREE = 2
norecursion = []
attributekeys = { 
                  NSSTR + 'dimension': 'direction',
                  NSSTR + 'direction': 'name',
                  NSSTR + 'reference': 'face',
                  NSSTR + 'plane': 'face'
                }
mergechildren = [NSSTR + 'actionlog', NSSTR + 'markings']


class SpecimenException(Exception):
    """ Error Handling Class for Specimen Database """
    pass


def GetSpecimen(specimen, output=OUTPUT_STRING):
    """ Fetch the XML Representation of a Specimen with Specimen Group Data Integrated """

    # Locate the Speicmen File
    filename = os.path.join(specimendb, specimen + '.sdb')
    if not os.path.exists(filename):
        raise SpecimenException('Unable to Locate Specimen Data File')
    elif not os.access(filename, os.R_OK):
        raise SpecimenException('Unable to Access Specimen Database')

    # Read the Specimen File
    try:
        f = open(filename, 'r')
        specimenxml = etree.XML(f.read())
        f.close()
    except:
        raise SpecimenException('Unable to Read Specimen Data File')

    # Identify the Group
    groupidelem = specimenxml.xpath("specimen:groupid", namespaces=NS)
    if len(groupidelem) > 1:
        raise SpecimenException('Multiple Group IDs Found - Feature Not Implemented')
    elif len(groupidelem) == 1:
        groupid = groupidelem[0].text

        # Locate the Group File
        filename = os.path.join(specimendb, groupid + '.sdg')
        if not os.path.exists(filename):
            if output == OUTPUT_STRING:
                print etree.tostring(specimenxml, pretty_print=True)
            elif output == OUTPUT_ELEMENT:
                return specimenxml
            elif output == OUTPUT_ETREE:
                return specimenxml.getroottree()
            else:
                raise SpecimenException('Invalid Return Type')
        elif not os.access(filename, os.R_OK):
            raise SpecimenException('Unable to Access Specimen Database')

        # Read Specimen Group File
        try:
            f = open(filename, 'r')
            groupxml = etree.XML(f.read())
            f.close()
        except:
            raise SpecimenException('Unable to Read Specimen Group Data File')

        # Combine Trees
        _combine_element(specimenxml, groupxml)

        # Output
        if output == OUTPUT_STRING:
            print etree.tostring(specimenxml, pretty_print=True)
        elif output == OUTPUT_ELEMENT:
            return specimenxml
        elif output == OUTPUT_ETREE:
            return specimenxml.getroottree()
        else:
            raise SpecimenException('Invalid Return Type')
        pass

    elif len(groupidelem) == 0:
        if output == OUTPUT_STRING:
            print etree.tostring(specimenxml, pretty_print=True)
        elif output == OUTPUT_ELEMENT:
            return specimenxml
        elif output == OUTPUT_ETREE:
            return specimenxml.getroottree()
        else:
            raise SpecimenException('Invalid Return Type')
    else:
        raise SpecimenException('Error Selecting Group ID Tag from Specimen Data File')

    pass

def tagname(el):
    if el.tag in attributekeys:
        return el.tag + el.get(attributekeys[el.tag])
    else:
        return el.tag

def _combine_element(one, other):
    """ Private Function to Recursively Combine etree Elements, Preferencing the First Element """
    mapping = {}
    for el in one:
        mapping[tagname(el)] = el
    for el in [el for el in other if tagname(el) not in [NSSTR + 'notes', NSSTR + 'specimenslist', NSSTR + 'identifiertags', NSSTR + 'groupid']]:
        if len(el) == 0 and not in norecursion and not in mergechildren:
            # Not nested
            if not tagname(el) in mapping:
                # An element with this name is not in the mapping
                mapping[tagname(el)] = el
                # Add it
                el.set('fromgroup', 'true')
                one.append(el)
            else:
                mapping[tagname(el)].set('override', 'true')

        else:
            if tagname(el) in norecursion:
                if not tagname(el) in mapping:
                     # Not in the mapping
                    mapping[tagname(el)] = el
                    el.set('fromgroup', 'true')
                    # Just add it
                    one.append(el)
                else:
                    mapping[tagname(el)].set('override', 'true')
            elif tagname(el) in mergechildren:
                if not tagname(el) in mapping:
                    mapping[tagname(el)] = el
                    for child in el:
                        el.set('fromgroup', 'true')
                    one.append(el)
                else:
                    for child in el:
                        child.set('fromgroup', 'true')
                        mapping[tagname(el)].append(child)
            else:   
                try:
                    # Recursively process the element, and update it in the same way
                    _combine_element(mapping[tagname(el)], el)
                except KeyError:
                    # Not in the mapping
                    mapping[tagname(el)] = el
                    el.set('fromgroup', 'true')
                    # Just add it
                    one.append(el)
    pass
