# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2011 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Plugin for displaying the exported version of a card set in a Gtk.TextView.
   Intended to make cutting and pasting easier."""

from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.base.gui.plugins.BaseShowExported import BaseShowExported
from sutekh.io.WriteJOL import WriteJOL
from sutekh.io.WriteLackeyCCG import WriteLackeyCCG
from sutekh.io.WriteELDBDeckFile import WriteELDBDeckFile
from sutekh.io.WriteArdbText import WriteArdbText
from sutekh.io.WritePmwiki import WritePmwiki
from sutekh.io.WriteVEKNForum import WriteVEKNForum

from sutekh.base.core.BaseTables import PhysicalCardSet
from sutekh.tests.GuiSutekhTest import LoadedGuiSutekhTest
from sutekh.tests.core.test_PhysicalCardSet import make_set_1
from sutekh.tests.io.test_WriteJOL import EXPECTED_1 as JOL_EXPECTED
from sutekh.tests.io.test_WriteArdbText import ARDB_TEXT_EXPECTED_1 as ARDB_EXPECTED


class ShowExported(SutekhPlugin, BaseShowExported):
    """Display the various exported versions of a card set."""

    EXPORTERS = BaseShowExported.EXPORTERS.copy()
    EXPORTERS.update({
        'Export to JOL format': WriteJOL,
        'Export to Lackey CCG format': WriteLackeyCCG,
        'Export to ARDB Text': WriteArdbText,
        'BBcode output for the V:EKN Forums': WriteVEKNForum,
        'Export to ELDB ELD Deck File': WriteELDBDeckFile,
        'Export to pmwiki': WritePmwiki,
    })


plugin = ShowExported


class TestShowExported(LoadedGuiSutekhTest):

    def setUp(self):
        super().setUp()
        self._oPhysSet = make_set_1()
        self.oWin.add_new_physical_card_set(self._oPhysSet.name)

    def test_output(self):
        oPane = self.oWin.find_cs_pane_by_set_name(self._oPhysSet.name)[0]
        oPlugin = ShowExported(oPane.view, oPane.view.get_model(), PhysicalCardSet)
        oDlg = oPlugin._make_dialog(self._oPhysSet)
        oBuffer = None
        aRadioButtons = []
        for oWidget in oDlg.get_children():
            for oChild in oWidget.get_children():
                 for oGrandChild in oChild.get_children():
                     if hasattr(oGrandChild, "get_group"):
                         aRadioButtons.append(oGrandChild)
                         continue
                     if hasattr(oGrandChild, "get_buffer"):
                         oBuffer = oGrandChild.get_buffer()
        # Check JOL
        for oBut in aRadioButtons:
             if 'JOL' in oBut.get_label():
                 oBut.set_active(True)
        sText = oBuffer.get_text(oBuffer.get_start_iter(), oBuffer.get_end_iter(), False)
        self.assertEqual(sText, JOL_EXPECTED)
        # Check ARDB
        for oBut in aRadioButtons:
             if 'ARDB Text' in oBut.get_label():
                 oBut.set_active(True)
        sText = oBuffer.get_text(oBuffer.get_start_iter(), oBuffer.get_end_iter(), False)
        self.assertEqual(sText, ARDB_EXPECTED)


test = TestShowExported
