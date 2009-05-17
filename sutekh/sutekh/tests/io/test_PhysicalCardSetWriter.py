# test_PhysicalCardSetWriter.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test Writing Card Set handling"""

from sutekh.tests.TestCore import SutekhTest
from sutekh.tests.core.test_PhysicalCardSet import CARD_SET_NAMES, \
        get_phys_cards
from sutekh.core.SutekhObjects import PhysicalCardSet
from sutekh.io.PhysicalCardSetWriter import PhysicalCardSetWriter
import unittest

EXPECTED = '<physicalcardset author="A test author" ' \
        'comment="A test comment" name="Test Set 1" '\
        'sutekh_xml_version="1.2">\n' \
        '  <annotations />\n' \
        '  <card count="1" expansion="None Specified" id="1"' \
        ' name=".44 Magnum" />\n' \
        '  <card count="1" expansion="None Specified" id="2"' \
        ' name="AK-47" />\n' \
        '  <card count="1" expansion="None Specified" id="8"' \
        ' name="Abbot" />\n' \
        '  <card count="1" expansion="None Specified" id="11"' \
        ' name="Abebe" />\n' \
        '  <card count="1" expansion="None Specified" id="14"' \
        ' name="Abombwe" />\n' \
        '</physicalcardset>'

class PhysicalCardSetWriterTests(SutekhTest):
    """class for the Physical Card Set writer tests"""

    def test_physical_card_set_writer(self):
        """Test physical card set writing"""
        # pylint: disable-msg=E1101, R0915, R0914
        # E1101: SQLObject + PyProtocols magic confuses pylint
        # R0915, R0914: Want a long, sequential test case to minimise
        # repeated setups, so it has lots of lines + variables
        aAddedPhysCards = get_phys_cards()
        # We have a physical card list, so create some physical card sets
        oPhysCardSet1 = PhysicalCardSet(name=CARD_SET_NAMES[0])
        oPhysCardSet1.comment = 'A test comment'
        oPhysCardSet1.author = 'A test author'

        for iLoop in range(5):
            oPhysCardSet1.addPhysicalCard(aAddedPhysCards[iLoop].id)
            oPhysCardSet1.syncUpdate()

        # Check output

        oWriter = PhysicalCardSetWriter()
        sWriterXML = oWriter.gen_xml_string(oPhysCardSet1.name)
        self.assertEqual(sWriterXML,
            oWriter.gen_xml_string(CARD_SET_NAMES[0]))
        # The writer uses database order - this is not
        # the same across databases, hence the nature of the checks below
        self.assertEqual(sWriterXML, EXPECTED)
        self.assertEqual(len(sWriterXML), len(EXPECTED))

        sTempFileName =  self._create_tmp_file()
        fOut = open(sTempFileName, 'w')
        oWriter.write(fOut, CARD_SET_NAMES[0])
        fOut.close()

        fIn = open(sTempFileName, 'rU')
        sData = fIn.read()
        self.assertEqual(sData, sWriterXML)
        self.assertEqual(len(sData), len(EXPECTED))
        self.assertEqual(sorted(sData), sorted(EXPECTED))

if __name__ == "__main__":
    unittest.main()