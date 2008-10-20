# test_ARDBXMLInvParser.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test reading a card set from an ARDB XML inventory file"""

import unittest
from sutekh.tests.TestCore import DummyHolder
from sutekh.io.ARDBXMLInvParser import ARDBXMLInvParser

class ArdbXMLInvParserTests(unittest.TestCase):
    """class for the ARDB XML inventory file parser tests"""

    # ARDB produces tag pairs for empty elements, we produce minimal
    # tags (<set></set> vs <set />, so we have both in the test data
    sTestText1 = """
    <inventory generator="Sutekh [ Test ]" fromatVersion="val">
        <date>2008-09-01</date>
        <crypt size="3">
            <vampire databaseID="1" have="2" spare="0" need="2">
               <name>Test Vamp 1</name>
               <adv></adv>
               <set>CE</set>
               <rarity>U2</rarity>
            </vampire>
            <vampire databaseID="2" have="1" spare="0" need="0">
               <name>Test Vamp 2</name>
               <adv></adv>
               <set>SW</set>
               <rarity>U</rarity>
            </vampire>
        </crypt>
        <library size="17">
           <card databaseID="3" have="4" spare="0" need="0">
              <name>Test Card 1</name>
              <set>Sabbat</set>
              <rarity>C</rarity>
           </card>
           <card databaseID="3" have="2" spare="0" need="0">
              <name>Test Card 2</name>
              <set>BH</set>
              <rarity>C</rarity>
           </card>
           <card databaseID="3" have="12" spare="0" need="0">
              <name>Test Card 3</name>
              <set>BH</set>
              <rarity>C</rarity>
           </card>
           <card databaseID="3" have="1" spare="0" need="0">
              <name>Test Card 4</name>
              <set></set>
              <rarity>C</rarity>
           </card>
        </library>
    </inventory>
    """

    def test_basic(self):
        """Run the input test."""
        oHolder = DummyHolder()
        oParser = ARDBXMLInvParser(oHolder)

        for sLine in self.sTestText1.split("\n"):
            oParser.feed(sLine + "\n")

        self.assertEqual(oHolder.name, "")

        aCards = oHolder.get_cards_exps()

        self.assertEqual(len(aCards), 6)
        self.failUnless((("Test Vamp 1", "CE"), 2) in aCards)
        self.failUnless((("Test Vamp 2", "SW"), 1) in aCards)
        self.failUnless((("Test Card 1", "Sabbat"), 4) in aCards)
        self.failUnless((("Test Card 2", "BH"), 2) in aCards)
        self.failUnless((("Test Card 3", "BH"), 12) in aCards)
        self.failUnless((("Test Card 4", None), 1) in aCards)

if __name__ == "__main__":
    unittest.main()
