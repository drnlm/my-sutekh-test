# WriteELDBInventory.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Writer for the FELDB inventory format.

   Example:

   "ELDB - Inventory"
   "Aabbt Kindred",1,0,"","Crypt"
   "Aaron Duggan, Cameron`s Toady",0,0,"","Crypt"
   ...
   "Zip Line",0,0,"","Library"
   """

import unicodedata
from sutekh.core.SutekhObjects import AbstractCard

def _type_of_card(oCard):
    """Return either Crypt or Library as required."""
    sType = list(oCard.cardtype)[0].name
    if sType == "Vampire" or sType == "Imbued":
        return "Crypt"
    else:
        return "Library"

def norm_name(oCard):
    """Transform a card name to the ELDB equivilant"""
    sName = oCard.name
    if oCard.level is not None:
        sName.replace("(Advanced)", "(ADV)")
    if sName.startswith("The ") and sName != "The Kikiyaon":
        # Annoying ELDB special case
        sName = sName[4:] + ", The"
    sName.replace("'", "`")
    return unicodedata.normalize('NFKD', sName).encode('ascii','ignore')

class WriteELDBInventory(object):
    """Create a string in ELDB inventory format representing a card set."""

    # pylint: disable-msg=R0201
    # method for consistency with the other methods
    def _gen_header(self):
        """Generate an ELDB inventory file header."""
        return '"ELDB - Inventory"'

    def _gen_inv(self, oCardSet):
        """Process the card set, creating the lines as needed"""
        dCards = {}
        sResult = ""
        for oCard in AbstractCard.select():
            dCards[oCard] = 0
        for oCard in oCardSet.cards:
            oAbsCard = oCard.abstractCard
            dCards[oAbsCard] += 1
        for oCard, iNum in dCards.iteritems():
            sResult += '"%s",%d,0,"","%s"\n' % (norm_name(oCard), iNum,
                    _type_of_card(oCard))
        return sResult

    # pylint: enable-msg=R0201

    def write(self, fOut, oCardSet):
        """Takes file object + card set to write, and writes an ELDB inventory
           representing the deck"""
        fOut.write(self._gen_header())
        fOut.write("\n")
        fOut.write(self._gen_inv(oCardSet))

    # pylint: enable-msg=R0913
