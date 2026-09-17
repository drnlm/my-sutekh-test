# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Dialog to display deck analysis software
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>,
# GPL - see COPYING for details
"""Calculate probabilities for drawing the current selection."""

from gi.repository import Gtk

from sutekh.SutekhUtility import is_crypt_card
from sutekh.gui.PluginManager import SutekhPlugin
from sutekh.base.core.BaseAdapters import IAbstractCard
from sutekh.base.gui.SutekhDialog import do_complaint_error
from sutekh.base.gui.plugins.BaseDrawProbabilities import BaseDrawProbPlugin

from mock import patch
from sutekh.base.core.BaseTables import PhysicalCardSet
from sutekh.base.tests.GuiTestUtils import cs_select_cards
from sutekh.tests.GuiSutekhTest import LoadedGuiSutekhTest
from sutekh.tests.core.test_PhysicalCardSet import make_set_1


class CardDrawSimPlugin(SutekhPlugin, BaseDrawProbPlugin):
    """Displays the probabilities for drawing cards from the current
       selection."""

    sHelpText = """This tool displays the probabilities of drawing the selected
                   cards from the library or the crypt. Unlike the _simulate
                   opening hand_ tool, this displays results for longer
                   sequences of card draws.

                   The first row of the table shows the probabilities of
                   drawing a single card in the selected list. Sub-rows show
                   the individual probabilities for each possible combination
                   of selected cards. The second row shows the probabilities of
                   drawing all possible combinations of two selected cards,
                   etc..

                   Each probability cell in the table displays two values: the
                   probability of drawing at least that combination of cards,
                   and the probability of drawing exactly that combination of
                   cards (shown in brackets).

                   The tool has the following settings:

                   * _columns in table_: Set the number of draws shown in \
                   the table. You must specify a number from one to eight \
                   (the default is eight). The first column shows the \
                   probabilities of drawing the given cards in your opening \
                   hand or crypt draw. Subsequent columns show the total \
                   probabilities of drawing the cards after you have drawn \
                   the number of extra cards shown in the column header.
                   * _step between columns_: Set the number of cards drawn \
                   between columns. You must specify a number from one to \
                   ten (the default is one).
                   * _cards of interest_: Set the number of rows in the \
                   table. You must specify a number from one to the total \
                   number of cards selected.

                   The selected changes are only applied when you press the
                   the _recalculate table_ button."""

    # pylint: disable=attribute-defined-outside-init
    # we define lots of things here, rather than __init__, since that's
    # how our override hooks work
    def _set_draw_title_and_size(self, oMainTitle):
        """Setup title and draw sizes"""
        if self.bCrypt:
            oMainTitle.set_markup('<b>Crypt:</b> Drawing from <b>%d</b> '
                                  'cards' % self.iTotal)
            self.iOpeningDraw = 4
            self.iNumSteps = min(2, self.iTotal - self.iOpeningDraw)
        else:
            oMainTitle.set_markup('<b>Library:</b> Drawing from <b>%d</b> '
                                  'cards' % self.iTotal)
            self.iOpeningDraw = 7
            self.iNumSteps = min(8, self.iTotal - self.iOpeningDraw)

    def _complain_size(self):
        """Correct complaint about the number of cards."""
        if self.bCrypt:
            do_complaint_error("Crypt must be larger than the opening draw")
        else:
            do_complaint_error("Library must be larger than the opening hand")

    def _setup_cardlists(self, aSelectedCards):
        """Extract the needed card info from the model"""
        aAllAbsCards = [IAbstractCard(oCard) for oCard in
                        self._get_all_cards()]
        iCryptSize = 0
        iLibrarySize = 0
        self.dSelectedCounts = {}
        self.iSelectedCount = 0
        # Initialise dict 1st, as cards with a count of 0 in the selection
        # are possible.
        for oCard in aSelectedCards:
            self.dSelectedCounts.setdefault(oCard, 0)
        for oCard in aAllAbsCards:
            if is_crypt_card(oCard):
                iCryptSize += 1
            else:
                iLibrarySize += 1
            if oCard in self.dSelectedCounts:
                self.dSelectedCounts[oCard] += 1
                self.iSelectedCount += 1
            # The assumption is that the user is interested in all copies of
            # the selected cards (as it seems the most useful), so we treat
            # the selection of any instance of the card in the list as
            # selecting all of them
        if self.bCrypt:
            self.iTotal = iCryptSize
        else:
            self.iTotal = iLibrarySize

    def _check_selection(self, aSelectedCards):
        """Check that selection is useable."""
        bCrypt = False
        bLibrary = False
        for oCard in aSelectedCards:
            # pylint: disable=simplifiable-if-statement
            # pylint misidentifies this because it misses the loop
            if is_crypt_card(oCard):
                bCrypt = True
            else:
                bLibrary = True
        # Check that selection doesn't mix crypt and libraries
        if bLibrary and bCrypt:
            do_complaint_error("Can't operate on selections including both"
                               " Crypt and Library cards")
            return False
        # Store this for later queries
        self.bCrypt = bCrypt
        return True

    def _get_table_draw_title(self):
        """Set the label for the results tabel"""
        if self.bCrypt:
            oLabel = Gtk.Label(label='Opening Draw')
        else:
            oLabel = Gtk.Label(label='Opening Hand')
        return oLabel


plugin = CardDrawSimPlugin



class TestCardDrawSim(LoadedGuiSutekhTest):

    def setUp(self):
        super().setUp()
        self._oPhysSet = make_set_1()
        self.oWin.add_new_physical_card_set(self._oPhysSet.name)


    def test_check_selected(self):
        oPane = self.oWin.find_cs_pane_by_set_name(self._oPhysSet.name)[0]
        oPlugin = CardDrawSimPlugin(oPane.view, oPane.view.get_model(), PhysicalCardSet)
        # Check that _check_selection fails when both crypt and library cards are selected
        with patch(f'{__name__}.do_complaint_error'):
            cs_select_cards(oPane, [('.44 Magnum', 'Jyhad'),
                                    ('The Siamese (Group 2)', 'Bloodlines')])
            aSelectedCards = oPlugin._get_selected_abs_cards()
            self.assertEqual(len(aSelectedCards), 2)
            bRes = oPlugin._check_selection(aSelectedCards)
            self.assertFalse(bRes)
        # Check that 2 library cards are OK
        with patch(f'{__name__}.do_complaint_error'):
            cs_select_cards(oPane, [('.44 Magnum', 'Jyhad'),
                                    ('Hide the Heart', 'Heirs to the Blood')])
            aSelectedCards = oPlugin._get_selected_abs_cards()
            self.assertEqual(len(aSelectedCards), 2)
            bRes = oPlugin._check_selection(aSelectedCards)
            self.assertTrue(bRes)
            self.assertFalse(oPlugin.bCrypt)
        # Check that 2 crypt cards are OK
        with patch(f'{__name__}.do_complaint_error'):
            cs_select_cards(oPane, [('Abebe (Group 4)', None),
                                    ('The Siamese (Group 2)', 'Bloodlines')])
            aSelectedCards = oPlugin._get_selected_abs_cards()
            self.assertEqual(len(aSelectedCards), 2)
            bRes = oPlugin._check_selection(aSelectedCards)
            self.assertTrue(bRes)
            self.assertTrue(oPlugin.bCrypt)

    def test_output(self):
        oPane = self.oWin.find_cs_pane_by_set_name(self._oPhysSet.name)[0]
        oPlugin = CardDrawSimPlugin(oPane.view, oPane.view.get_model(), PhysicalCardSet)
        # Select cards
        cs_select_cards(oPane, [('.44 Magnum', ),
                                ('Hide the Heart', ),
                                ('Immortal Grapple', )])

        # Do the steps needed for tests
        aSelectedCards = oPlugin._get_selected_abs_cards()

        bRes = oPlugin._check_selection(aSelectedCards)
        oPlugin._setup_cardlists(aSelectedCards)

        oLabel = Gtk.Label()
        oPlugin._set_draw_title_and_size(oLabel)

        oPlugin._set_initial_values()

        oDlg = oPlugin._make_dialog(oLabel)
        oPlugin._fill_table(None)

        oBuffer = None
        aRadioButtons = []
        oDlg.show_all()
        aTableText = []
        # Get all the table text
        # We don't preserve the structure of the table well here,
        # since we just getting the children
        # FIXME: When we replace Gtk.Table with Gtk.Grid, we can
        # do better here
        for oChild in oPlugin.oResultsTable.get_children():
            if hasattr(oChild, 'get_text'):
                aTableText.append(oChild.get_text())

        # Find some of the expected card combos
        self.assertIn("1 × Immortal Grapple\n1 × .44 Magnum\n1 × Hide the Heart\n", aTableText)
        self.assertIn("3 × Immortal Grapple\n0 × .44 Magnum\n0 × Hide the Heart\n", aTableText)
        self.assertIn("0 × Immortal Grapple\n0 × .44 Magnum\n1 × Hide the Heart\n", aTableText)
        self.assertIn("None of the cards", aTableText)
        # Check some of the expected headers
        self.assertIn("+ 7", aTableText)
        self.assertIn("Opening Hand", aTableText)
        self.assertIn("Number of cards seen", aTableText)
        # Check we have all the expected entries
        iExpected = 16*9   # 16 card combination - 9 rows for each
        iExpected += 7 + 4 # the +1 .. + 7 labels and the 0,1,2,3 groupings
        iExpected += 2     # The 'Opening Hand ' & 'Count' labels
        iExpected += 2     # The 'Cards Drawn' & 'Number Seen' labels
        self.assertEqual(len(aTableText), iExpected)


test = TestCardDrawSim
