# test_ELDBDeckFileParser.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test reading a card set from an ELDB deck file"""

import unittest
from sutekh.tests.TestCore import SutekhTest
from sutekh.io.ELDBDeckFileParser import ELDBDeckFileParser

class DummyHolder(object):
    """Emulate CardSetHolder for test purposes."""
    def __init__(self):
        self.dCards = {}
        # pylint: disable-msg=C0103
        # placeholder names for CardSetHolder attributes
        self.name = ''
        self.comment = ''
        self.author = ''

    # pylint: disable-msg=W0613
    # sExpName is unused, but needed to make function signature match
    def add(self, iCnt, sName, sExpName):
        """Add a card to the dummy holder."""
        self.dCards.setdefault(sName, 0)
        self.dCards[sName] += iCnt


class TestELDBDeckFileParser(SutekhTest):
    """class for the ELDB deck file parser tests"""

    sTestText1 = """
        "Test Deck"
        "Anon Y Mous"
        "Simple test deck.

        http://www.example.url/in/description"
        3
        "Test Vamp 1"
        "Test Vamp 1"
        "Lazar Dobrescu"
        17
        "Test Card 1"
        "Test Card 1"
        "Test Card 2"
        "Test Card 2"
        "Test Card 2"
        "Test Card 2"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 3"
        "Test Card 4"
        """

    def test_basic(self):
        """Run the input test."""
        oHolder = DummyHolder()
        oParser = ELDBDeckFileParser(oHolder)

        for sLine in self.sTestText1.split("\n"):
            oParser.feed(sLine + "\n")

        self.assertEqual(oHolder.name, "Test Deck")
        self.assertEqual(oHolder.author, "Anon Y Mous")
        self.failUnless(oHolder.comment.startswith(
            "Simple test deck."))
        self.failUnless(oHolder.comment.endswith("in/description"))

        aCards = oHolder.dCards.items()

        self.assertEqual(len(aCards), 6)
        self.failUnless(("Test Vamp 1", 2) in aCards)
        self.failUnless((u"L\xe1z\xe1r Dobrescu", 1) in aCards)
        self.failUnless(("Test Card 1", 2 ) in aCards)
        self.failUnless(("Test Card 2", 4) in aCards)
        self.failUnless(("Test Card 3", 12) in aCards)
        self.failUnless(("Test Card 4", 1) in aCards)

if __name__ == "__main__":
    unittest.main()
