# CardSetManagementFrame.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Window for Managing Physical and Abstract Card Sets
# Copyright 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""Pane for a list of card sets"""

import gtk
from sqlobject import SQLObjectNotFound
from sutekh.SutekhUtility import delete_physical_card_set
from sutekh.core.SutekhObjects import PhysicalCardSet
from sutekh.core.Filters import NullFilter
from sutekh.gui.SutekhDialog import do_complaint_warning
from sutekh.gui.BasicFrame import BasicFrame
from sutekh.gui.CreateCardSetDialog import CreateCardSetDialog
from sutekh.gui.CardSetManagementMenu import CardSetManagementMenu
from sutekh.gui.CardSetManagementView import CardSetManagementView
from sutekh.gui.AutoScrolledWindow import AutoScrolledWindow

class CardSetManagementFrame(BasicFrame):
    # pylint: disable-msg=R0904
    # gtk.Widget, so lots of public methods
    """Pane for the List of card sets.

       Provides the actions associated with this Pane - creating new
       card sets, filtering, etc.
       """
    _sFilterType = 'PhysicalCardSet'
    _sName = 'Card Set List'
    _oSetClass = PhysicalCardSet

    def __init__(self, oMainWindow):
        super(CardSetManagementFrame, self).__init__(oMainWindow)
        self._oFilter = NullFilter()
        self._oFilterDialog = None
        self._oMenu = None
        self._oView = CardSetManagementView(oMainWindow)
        self.set_name("card sets list")
        self.add_parts()

    # pylint: disable-msg=W0212
    # We allow access via these properties
    type = property(fget=lambda self: self._sName, doc="Frame Type")
    menu = property(fget=lambda self: self._oMenu, doc="Frame Menu")
    # pylint: enable-msg=W0212

    def add_parts(self):
        """Add a list object to the frame"""
        oMbox = gtk.VBox(False, 2)

        self.set_title(self._sName)
        oMbox.pack_start(self._oTitle, False, False)

        self._oMenu = CardSetManagementMenu(self, self._oMainWindow,
                self._oView)

        oMbox.pack_start(self._oMenu, False, False)

        oMbox.pack_start(AutoScrolledWindow(self._oView), expand=True)

        # setup default targets
        self.set_drag_handler()

        self.add(oMbox)
        self.show_all()

    def reload(self):
        """Reload the frame contents"""
        self._oView.reload_keep_expanded(True)

    # pylint: disable-msg=W0613
    # oWidget, oMenuItem required by function signature
    def create_new_card_set(self, oWidget):
        """Create a new card set"""
        oDialog = CreateCardSetDialog(self._oMainWindow)
        oDialog.run()
        sName = oDialog.get_name()
        # pylint: disable-msg=E1102, W0612
        # W0612 - oCS isn't important, as the creation of the new card
        # set is what matters
        if sName:
            sAuthor = oDialog.get_author()
            sComment = oDialog.get_comment()
            oParent = oDialog.get_parent()
            oCS = PhysicalCardSet(name=sName, author=sAuthor,
                    comment=sComment, parent=oParent)
            self._oMainWindow.add_new_physical_card_set(sName)

    def delete_card_set(self, oWidget):
        """Delete the selected card set."""
        sSetName = self._oView.get_selected_card_set()
        if not sSetName:
            return
        # pylint: disable-msg=E1101
        # sqlobject confuses pylint
        try:
            oCS = PhysicalCardSet.byName(sSetName)
        except SQLObjectNotFound:
            return
        if len(oCS.cards) > 0:
            iResponse = do_complaint_warning("Card Set %s Not Empty. Really"
                    " Delete?" % sSetName)
            if iResponse == gtk.RESPONSE_CANCEL:
                # Don't delete
                return
        # Got here, so delete the card set
        sFrameName = sSetName
        delete_physical_card_set(sSetName)
        self._oMainWindow.remove_frame_by_name(sFrameName)
        self.reload()

    def toggle_in_use_flag(self, oMenuItem):
        """Toggle the in-use status of the card set"""
        sSetName = self._oView.get_selected_card_set()
        if not sSetName:
            return
        try:
            # pylint: disable-msg=E1101
            # SQLObject confuses pylint
            oCS = PhysicalCardSet.byName(sSetName)
        except SQLObjectNotFound:
            return
        oCS.inuse = not oCS.inuse
        oCS.syncUpdate()
        self._oView.reload_keep_expanded(True)
