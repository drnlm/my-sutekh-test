# test_PhysicalCardSetParser.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test Card Set reading from file"""

from sutekh.tests.TestCore import SutekhTest
from sutekh.core.SutekhObjects import IAbstractCard, IPhysicalCard, \
        IExpansion, IPhysicalCardSet, MapPhysicalCardToPhysicalCardSet
from sutekh.io.PhysicalCardSetParser import PhysicalCardSetParser
import unittest

class PhysicalCardSetParserTests(SutekhTest):
    """class for the Card Set Parser tests"""
    aAbstractCards = ['.44 magnum', 'ak-47', 'abbot', 'abebe', 'abombwe']
    aCardExpansions = [('.44 magnum', 'Jyhad'),
            ('ak-47', 'LotN'),
            ('abbot', 'Third Edition'),
            ('abombwe', 'Legacy of Blood')]
    aCardSetNames = ['Test Set 1', 'Test Set 2']

    def _get_phys_cards(self):
        """Fill contents of the physical card table"""
        aAddedPhysCards = []
        for sName in self.aAbstractCards:
            oAC = IAbstractCard(sName)
            oPC = IPhysicalCard((oAC, None))
            aAddedPhysCards.append(oPC)
        for sName, sExpansion in self.aCardExpansions:
            oAC = IAbstractCard(sName)
            oExpansion = IExpansion(sExpansion)
            oPC = IPhysicalCard((oAC, oExpansion))
            aAddedPhysCards.append(oPC)
        return aAddedPhysCards

    def test_physical_card_set_parser(self):
        """Test physical card set reading"""
        # pylint: disable-msg=E1101, R0915, R0914
        # E1101: SQLObject + PyProtocols magic confuses pylint
        # R0915, R0914: Want a long, sequentila test case to minimise
        # repeated setups, so it has lots of lines + variables
        aAddedPhysCards = self._get_phys_cards()
        # We have a physical card list, so create some physical card sets

        sExpected1 = '<physicalcardset author="A test author" ' \
                'comment="A test comment" name="Test Set 1" '\
                'sutekh_xml_version="1.2"><annotations /><card count="1" ' \
                'expansion="None Specified" id="11" name="Abebe" /><card ' \
                'count="1" expansion="None Specified" id="1" ' \
                'name=".44 Magnum" /><card count="1" expansion="None ' \
                'Specified" id="8" name="Abbot" /><card count="1" ' \
                'expansion="None Specified" id="2" name="AK-47" /><card ' \
                'count="1" expansion="None Specified" id="14" ' \
                'name="Abombwe" /></physicalcardset>'

        sExpected2 = '<physicalcardset author="A test author" ' \
                'comment="A test comment" name="Test Set 2" '\
                'sutekh_xml_version="1.2"><annotations />\n"' \
                '<card count="1" expansion="None Specified" id="8" ' \
                'name="Abbot" />\n' \
                '<card count="2" expansion="None Specified" id="2" ' \
                'name="AK-47" />\n' \
                '<card count="1" expansion="None Specified" id="14" ' \
                'name="Abombwe" />\n' \
                '<card count="1" expansion = "Jyhad" id="1" ' \
                'name=".44 Magnum" />\n' \
                '<card count="1" expansion="Lords of the Night" id="2" ' \
                'name="AK-47" />\n</physicalcardset>'

        # Check input

        oParser = PhysicalCardSetParser()

        oParser.parse_string(sExpected1)

        sFileName = self._create_tmp_file()
        fIn = open(sFileName, 'w')
        fIn.write(sExpected2)
        fIn.close()
        fIn = open(sFileName, 'r')
        oParser.parse(fIn)
        fIn.close()

        oPhysCardSet1 = IPhysicalCardSet(self.aCardSetNames[0])
        oPhysCardSet2 = IPhysicalCardSet(self.aCardSetNames[1])

        self.assertEqual(len(oPhysCardSet1.cards), 5)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[0].id).count(), 1)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[7].id).count(), 0)
        self.assertEqual(len(oPhysCardSet2.cards), 6)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[4].id).count(), 2)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[0].id).count(), 1)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[1].id).count(), 3)
        self.assertEqual(MapPhysicalCardToPhysicalCardSet.selectBy(
            physicalCardID = aAddedPhysCards[6].id).count(), 1)


if __name__ == "__main__":
    unittest.main()
