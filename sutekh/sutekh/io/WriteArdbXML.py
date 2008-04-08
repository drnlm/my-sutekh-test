# WriteArdbXML.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# Based off the Anarach Revolt Deck Builder xml support,
# ARDB (c) Francios Gombalt, Christoph Boget, Ville Virta and Vincent Ripoll
# GPL - see COPYING for details

"""
Give a list of Abstract Cards in a set, write a XML file compatable with
the Anarch Revolt Deck Builder
"""

from sutekh.core.SutekhObjects import IAbstractCard
from sutekh.SutekhInfo import SutekhInfo
from sutekh.SutekhUtility import pretty_xml
import time
try:
    # pylint: disable-msg=E0611, F0401
    # xml.etree is a python2.5 thing
    from xml.etree.ElementTree import Element, SubElement, ElementTree, \
            tostring
except ImportError:
    from elementtree.ElementTree import Element, SubElement, ElementTree, \
            tostring

# helper functions
# card information functions
def get_disciplines(oCard):
    """Extract the discipline string from the card."""
    if len(oCard.discipline) > 0:
        aDisc = []
        for oDisc in oCard.discipline:
            if oDisc.level == 'superior':
                aDisc.append(oDisc.discipline.name.upper())
            else:
                aDisc.append(oDisc.discipline.name)
        aDisc.sort() # May not be needed
        return " ".join(aDisc)
    elif len(oCard.virtue) > 0:
        return " ".join([x.name for x in oCard.virtue])
    return ""

def extract_crypt(dCards):
    """Extract the crypt cards from the list."""
    iCryptSize = 0
    iMax = 0
    iMin = 75
    fAvg = 0.0
    dVamps = {}
    for tKey, iCount in dCards.iteritems():
        sName = tKey[1]
        # pylint: disable-msg=E1101
        # IAbstractCard confuses pylint
        oCard = IAbstractCard(sName)
        aTypes = [x.name for x in oCard.cardtype]
        if aTypes[0] == 'Vampire':
            dVamps[tKey] = iCount
            iCryptSize += iCount
            fAvg += oCard.capacity*iCount
            if oCard.capacity > iMax:
                iMax = oCard.capacity
            if oCard.capacity < iMin:
                iMin = oCard.capacity
        if aTypes[0] == 'Imbued':
            dVamps[tKey] = iCount
            iCryptSize += iCount
            fAvg += oCard.life*iCount
            if oCard.capacity > iMax:
                iMax = oCard.life
            if oCard.capacity < iMin:
                iMin = oCard.life
    if iCryptSize > 0:
        fAvg = round(fAvg/iCryptSize, 2)
    if iMin == 75:
        iMin = 0
    return (dVamps, iCryptSize, iMin, iMax, fAvg)

def extract_library(dCards):
    """Extract the library cards from the list."""
    iSize = 0
    dLib = {}
    for tKey, iCount in dCards.iteritems():
        iId, sName = tKey
        # pylint: disable-msg=E1101
        # IAbstractCard confuses pylint
        oCard = IAbstractCard(sName)
        aTypes = [x.name for x in oCard.cardtype]
        if aTypes[0] != 'Vampire' and aTypes[0] != 'Imbued':
            # Looks like it should be the right thing, but may not
            sTypeString = "/".join(aTypes)
            # We want to be able to sort over types easily, so
            # we add them to the keys
            dLib[(iId, sName, sTypeString)] = iCount
            iSize += iCount
    return (dLib, iSize)

# Element creation functions

def format_vamps(oCryptElem, dVamps):
    """Convert the Vampire dictionary into elementtree representation."""
    # pylint: disable-msg=R0914
    # Need this many local variables to create proper XML tree
    for tKey, iNum in dVamps.iteritems():
        iId, sName = tKey
        # pylint: disable-msg=E1101
        # IAbstractCard confuses pylint
        oCard = IAbstractCard(sName)
        oCardElem = SubElement(oCryptElem, 'vampire',
                databaseID=str(iId), count=str(iNum))
        # This won't match the ARDB ID's, unless by chance.
        # It looks like that should not be an issue as ARDB will
        # use the name if the IDs don't match
        # It's unclear to me what values ARDB uses here, but
        # these are fine for the xml2html conversion, and look meaningful
        oAdvElem = SubElement(oCardElem, 'adv')
        oNameElem = SubElement(oCardElem, 'name')
        if oCard.level is not None:
            oAdvElem.text = '(Advanced)'
            # This is a bit hackish
            oNameElem.text = sName.replace(' (Advanced)', '')
        else:
            oNameElem.text = sName
        oDiscElem = SubElement(oCardElem, 'disciplines')
        sDisciplines = get_disciplines(oCard)
        oDiscElem.text = sDisciplines
        aClan = [x.name for x in oCard.clan]
        oClanElem = SubElement(oCardElem, 'clan')
        oCapElem = SubElement(oCardElem, 'capacity')
        if len(oCard.creed) > 0:
            # ARDB seems to treat all Imbued as being of the same clan
            # Should we do an Imbued:Creed thing?
            oClanElem.text = 'Imbued'
            oCapElem.text = str(oCard.life)
        else:
            oClanElem.text = aClan[0]
            oCapElem.text = str(oCard.capacity)
        oGrpElem = SubElement(oCardElem, 'group')
        oGrpElem.text = str(oCard.group)
        # ARDB doesn't handle sect specifically
        # No idea how ARDB represents independant titles -
        # this seems set when the ARDB database is created, and is
        # not in the ARDB codebase
        if len(oCard.title) > 0:
            oTitleElem = SubElement(oCardElem, 'title')
            aTitles = [oC.name for oC in oCard.title]
            oTitleElem.text = aTitles[0]
        oTextElem = SubElement(oCardElem, 'text')
        oTextElem.text = oCard.text

def format_library(oLibElem, dLib):
    """Format the dictionary of library cards for the element tree."""
    # pylint: disable-msg=R0914
    # Need this many local variables to create proper XML tree
    for tKey, iNum in dLib.iteritems():
        iId, sName, sTypeString = tKey
        # pylint: disable-msg=E1101
        # IAbstractCard confuses pylint
        oCard = IAbstractCard(sName)
        oCardElem = SubElement(oLibElem, 'card', databaseID=str(iId),
                count=str(iNum))
        oNameElem = SubElement(oCardElem, 'name')
        oNameElem.text = sName
        if oCard.costtype is not None:
            oCostElem = SubElement(oCardElem, 'cost')
            oCostElem.text = "%d %s " % (oCard.cost, oCard.costtype )
        if len(oCard.clan) > 0:
            # ARDB also strores things like "requires a prince"
            # we don't so too bad
            oReqElem = SubElement(oCardElem, 'requirement')
            aClan = [x.name for x in oCard.clan]
            oReqElem.text = "/".join(aClan)
        oTypeElem = SubElement(oCardElem, 'type')
        oTypeElem.text = sTypeString
        # Not sure if this does quite the right thing here
        sDisciplines = get_disciplines(oCard)
        if sDisciplines != '':
            oDiscElem = SubElement(oCardElem, 'disciplines')
            oDiscElem.text = sDisciplines
        oTextElem = SubElement(oCardElem, 'text')
        oTextElem.text = oCard.text

class WriteArdbXML(object):
    """Reformat cardset to elementTree and export it to a ARDB
       compatible XML file."""

    # Should this be an attribute of VersionTable?
    sDatabaseVersion = 'Sutekh-20071201'
    # pylint: disable-msg=W0511
    # this is not a actual TODO item
    # Claim same version as recent ARDB
    sFormatVersion = '-TODO-1.0'
    # pyline: enable-msg=W0511

    def gen_tree(self, sSetName, sAuthor, sDescription, dCards):
        """Creates the actual XML document into memory."""
        # pylint: disable-msg=R0914
        # Need this many local variables to create proper XML tree
        oRoot = Element('deck')

        sDateWritten = time.strftime('%Y-%m-%d', time.localtime())
        oRoot.attrib['generator'] = "Sutekh [ %s ]" % SutekhInfo.VERSION_STR
        oRoot.attrib['formatVersion'] = self.sFormatVersion
        oRoot.attrib['databaseVersion'] = self.sDatabaseVersion
        oNameElem = SubElement(oRoot, 'name')
        oNameElem.text  = sSetName
        oAuthElem = SubElement(oRoot, 'author')
        oAuthElem.text = sAuthor
        oDescElem = SubElement(oRoot, 'description')
        oDescElem.text = sDescription
        oDateElem = SubElement(oRoot, 'date')
        oDateElem.text = sDateWritten

        (dVamps, iCryptSize, iMin, iMax, fAvg) = extract_crypt(dCards)
        (dLib, iLibSize) = extract_library(dCards)

        oCryptElem = SubElement(oRoot, 'crypt', size=str(iCryptSize),
                min=str(iMin), max=str(iMax), avg=str(fAvg))
        format_vamps(oCryptElem, dVamps)

        oLibElem = SubElement(oRoot, 'library', size=str(iLibSize))
        format_library(oLibElem, dLib)

        return oRoot

    # pylint: disable-msg=R0913
    # we need all these arguments
    def write(self, fOut, sSetName, sAuthor, sDescription, dCards):
        """
        Takes filename, deck details and a dictionary of cards, of the form
        dCard[(id,name)]=count
        """
        oRoot = self.gen_tree(sSetName, sAuthor, sDescription, dCards)
        pretty_xml(oRoot)
        ElementTree(oRoot).write(fOut)

    # pylint: enable-msg=R0913

    def gen_xml_string(self, sSetName, sAuthor, sDescription, dCards):
        """Generate string XML representation"""
        oRoot = self.gen_tree(sSetName, sAuthor, sDescription, dCards)
        return tostring(oRoot)


