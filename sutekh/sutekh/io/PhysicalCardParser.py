# PhysicalCardParser.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2005, 2006, 2007 Simon Cross <hodgestar@gmail.com>
# Copyright 2007, 2008 Neil Muller <drnlmuller+sutekh@gmail.com> 
# GPL - see COPYING for details

"""
Read physical cards from an XML file which
looks like:
<cards sutekh_xml_version="1.0">
  <card id='3' name='Some Card' count='5' expansion="Some Expansion" />
  <card id='3' name='Some Card' count='2' Expansion="Some Other Expansion" />
  <card id='5' name='Some Other Card' count='2' expansion="Some Expansion" />
</cards>
"""

from sutekh.core.SutekhObjects import IExpansion
from sutekh.core.CardSetHolder import CardSetHolder
from sutekh.core.CardLookup import DEFAULT_LOOKUP
from sqlobject import sqlhub
try:
    from xml.etree.ElementTree import parse, fromstring, ElementTree
except ImportError:
    from elementtree.ElementTree import parse, fromstring, ElementTree

class PhysicalCardParser(object):
    aSupportedVersions = ['1.0', '0.0']

    def __init__(self):
        self.oCS = CardSetHolder()
        self.oTree = None

    def _convertTree(self):
        """parse the elementtree into a card set holder"""
        oRoot = self.oTree.getroot()
        if oRoot.tag != 'cards':
            raise RuntimeError("Not a Physical card list")
        if oRoot.attrib['sutekh_xml_version'] not in self.aSupportedVersions:
            raise RuntimeError("Unrecognised XML File version")
        for oElem in oRoot:
            if oElem.tag == 'card':
                iCount = int(oElem.attrib['count'], 10)
                sName = oElem.attrib['name']
                try:
                    sExpansionName = oElem.attrib['expansion']
                except KeyError:
                    sExpansionName = 'None Specified'
                if sExpansionName == 'None Specified':
                    self.oCS.add(iCount, sName, None)
                else:
                    oExpansion = IExpansion(sExpansionName)
                    self.oCS.add(iCount, sName, oExpansion)

    def _commitTree(self, oCardLookup):
        """Commit contents of the card set holder to
           the database"""
        oOldConn = sqlhub.processConnection
        sqlhub.processConnection = oOldConn.transaction()
        self.oCS.createPhysicalCardList(oCardLookup)
        sqlhub.processConnection.commit()
        sqlhub.processConnection = oOldConn

    def parse(self, fIn, oCardLookup=DEFAULT_LOOKUP):
        self.oTree = parse(fIn)
        self._convertTree()
        self._commitTree(oCardLookup)

    def parse_string(self, sIn, oCardLookup=DEFAULT_LOOKUP):
        self.oTree = ElementTree(fromstring(sIn))
        self._convertTree()
        self._commitTree(oCardLookup)
