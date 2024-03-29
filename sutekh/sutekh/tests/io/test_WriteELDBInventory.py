# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Test Writing a card set to an ELDB Inventory"""

import unittest

from sutekh.base.core.CardSetHolder import CardSetWrapper

from sutekh.io.WriteELDBInventory import WriteELDBInventory
from sutekh.tests.TestCore import SutekhTest
from sutekh.tests.core.test_PhysicalCardSet import make_set_1

EXPECTED = """"ELDB - Inventory"
"Anastasz di Zagreb",0,0,"","Crypt"
"Alfred Benezri",0,0,"","Crypt"
"Bronwen",0,0,"","Crypt"
"Akram",0,0,"","Crypt"
"Lazar Dobrescu",0,0,"","Crypt"
"Aaron`s Feeding Razor",1,0,"","Library"
"Inez 'Nurse216' Villagrande",1,0,"","Crypt"
"Angelica, The Canonicus",0,0,"","Crypt"
"Abdelsobek",0,0,"","Crypt"
"Aeron",0,0,"","Crypt"
"Aaron Bathurst",0,0,"","Crypt"
"Aaron Duggan, Cameron`s Toady",0,0,"","Crypt"
"Kemintiri (ADV)",0,0,"","Crypt"
"Predator`s Communion",0,0,"","Library"
"Abombwe",2,0,"","Library"
"Alabastrom",0,0,"","Crypt"
"Alan Sovereign (ADV)",1,0,"","Crypt"
"Anna 'Dictatrix11' Suljic",0,0,"","Crypt"
"Gracis Nostinus",0,0,"","Crypt"
"Aire of Elation",3,0,"","Library"
"Amisa",0,0,"","Crypt"
".44 Magnum",4,0,"","Library"
"Ambrogino Giovanni",0,0,"","Crypt"
"Abebe",1,0,"","Crypt"
"Cedric",0,0,"","Crypt"
"Kabede Maru",0,0,"","Crypt"
"Cesewayo",0,0,"","Crypt"
"Alan Sovereign",0,0,"","Crypt"
"Ablative Skin",0,0,"","Library"
"Abbot",2,0,"","Library"
"Alexandra",0,0,"","Crypt"
"Abd al-Rashid",0,0,"","Crypt"
"Slaughterhouse, The",0,0,"","Library"
"Path of Blood, The",1,0,"","Library"
"Sha-Ennu",0,0,"","Crypt"
"Siamese, The",2,0,"","Crypt"
"Aabbt Kindred",0,0,"","Crypt"
"Abandoning the Flesh",0,0,"","Library"
"AK-47",2,0,"","Library"
"Abjure",0,0,"","Library"
"Ghoul Retainer",0,0,"","Library"
"Yvette, The Hopeless",0,0,"","Crypt"
"Anson",0,0,"","Crypt"
"Ashur Tablets",0,0,"","Library"
"Earl 'Shaka74' Deams",0,0,"","Crypt"
"Raven Spy",0,0,"","Library"
"Pariah",0,0,"","Crypt"
"Shade",0,0,"","Library"
"Ankara Citadel, Turkey, The",0,0,"","Library"
"Gypsies",0,0,"","Library"
"Agent of Power",0,0,"","Library"
"Swallowed by the Night",2,0,"","Library"
"Two Wrongs",0,0,"","Library"
"Scapelli, The Family `Mechanic`",1,0,"","Library"
"Political Hunting Ground",0,0,"","Library"
"Living Manse",0,0,"","Library"
"Paris Opera House",0,0,"","Library"
"Vox Domini",0,0,"","Library"
"Park Hunting Ground",0,0,"","Library"
"High Top",0,0,"","Library"
"Pier 13, Port of Baltimore",0,0,"","Library"
"Ossian",0,0,"","Library"
"Necromancy",0,0,"","Library"
"Rock Cat",0,0,"","Library"
"Enkidu, The Noah",0,0,"","Crypt"
"Fidus, The Shrunken Beast",0,0,"","Crypt"
"Rebekka, Chantry Elder of Munich",0,0,"","Crypt"
"Protracted Investment",0,0,"","Library"
"Bravo",0,0,"","Library"
"Dramatic Upheaval",0,0,"","Library"
"Motivated by Gehenna",0,0,"","Library"
"Hide the Heart",1,0,"","Library"
"Anarch Railroad",0,0,"","Library"
"Anarch Revolt",0,0,"","Library"
"Smite",0,0,"","Library"
"Aye",0,0,"","Library"
"New Blood",0,0,"","Crypt"
"Off Kilter",0,0,"","Library"
"Anarch Manifesto, An",1,0,"","Library"
"Walk of Flame",4,0,"","Library"
"Immortal Grapple",4,0,"","Library"
"Harold Zettler, Pentex Director",0,0,"","Crypt"
"Hektor",1,0,"","Crypt"
"Sheela Na Gig",0,0,"","Crypt"
"Etienne Fauberge",0,0,"","Crypt"
"Baron Dieudonne",0,0,"","Crypt"
"Crow",0,0,"","Crypt"
"Claudia",0,0,"","Crypt"
"Count Jocalo",0,0,"","Crypt"
"Rise of the Fallen",0,0,"","Library"
"Victoria Ash",0,0,"","Crypt"
"Victoria Ash (Group 7)",0,0,"","Crypt"
"Pentex(TM) Subversion",0,0,"","Library"
"Theo Bell",0,0,"","Crypt"
"Theo Bell (ADV)",0,0,"","Crypt"
"Theo Bell (Group 6)",0,0,"","Crypt"
"Wake with Evening`s Freshness",0,0,"","Library"
"Telepathic Counter",0,0,"","Library"
"My Enemy`s Enemy",0,0,"","Library"
"Enhanced Senses",0,0,"","Library"
"Eyes of Argus",0,0,"","Library"
"Ambush",0,0,"","Library"
"Bait and Switch",0,0,"","Library"
"Deep Song",0,0,"","Library"
"Deflection",0,0,"","Library"
"Govern the Unaligned",0,0,"","Library"
"""


class ELDBInventoryWriterTests(SutekhTest):
    """class for the ELDB Inventory writer tests"""
    # pylint: disable=too-many-public-methods
    # unittest.TestCase, so many public methods

    def test_inventory_writer(self):
        """Test ELDB inventory writing"""
        self.maxDiff = None
        oPhysCardSet1 = make_set_1()

        # Check output

        oWriter = WriteELDBInventory()
        sData = self._round_trip_obj(oWriter, CardSetWrapper(oPhysCardSet1))

        self.assertEqual(sorted(sData.splitlines()),
                         sorted(EXPECTED.splitlines()),
                         "Output differs : %s vs %s" % (
                             sorted(sData.splitlines()),
                             sorted(EXPECTED.splitlines())))


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
