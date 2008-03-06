# MultiSelectComboBox.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Generic multiselect combobox for use in FilterEditor (and elsewhere)"""

import gtk, gobject
from sutekh.gui.AutoScrolledWindow import AutoScrolledWindow

class MultiSelectComboBox(gtk.HBox):
    """
    Implementation of a multiselect combo box widget.
    """

    def __init__(self):
        super(MultiSelectComboBox, self).__init__()

        self._oButton = gtk.Button(" - ")
        self._oButton.connect('clicked', self.__show_list)
        self.pack_start(self._oButton)

        self._oListStore = gtk.ListStore(gobject.TYPE_STRING)

        self._oTreeView = gtk.TreeView(self._oListStore)
        oCell1 = gtk.CellRendererText()
        oColumn1 = gtk.TreeViewColumn(" ... ", oCell1, markup=0)
        self._oTreeView.append_column(oColumn1)
        self._oTreeView.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        self._oScrolled = AutoScrolledWindow(self._oTreeView)

        self._oDialog = gtk.Dialog("Select ...", None, gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_DESTROY_WITH_PARENT)
        self._oDialog.set_decorated(False)
        self._oDialog.action_area.set_size_request(-1, 0)
        self._oDialog.vbox.pack_start(self._oScrolled)
        self._oDialog.connect('key-press-event', self.__hide_on_return)

        # TODO: Hook up row_activate so that double-clicking selects the item and closes the list

    def __show_list(self, oButton):
        self._aOldSelection = self.get_selection()

        oParent = self.get_parent_window()

        tWinPos = oParent.get_origin() # Need coordinates relative to root window
        tButtonPos = (self._oButton.allocation.x, self._oButton.allocation.y)
        tShift = (5, self._oButton.allocation.height)

        tDialogPos = ( tWinPos[0] + tButtonPos[0] + tShift[0],
                       tWinPos[1] + tButtonPos[1] + tShift[1] )

        self._oDialog.set_keep_above(True) # Keep this above the dialog
        self._oDialog.show_all()
        # WM behaviour means that move is unlikely to work before _oDialog is shown
        self._oDialog.move(*tDialogPos)

    def __hide_list(self):
        self._oDialog.hide_all()
        self._oButton.set_label(", ".join(self.get_selection()))

    def __hide_on_return(self, oWidget, oEvent):
        if oEvent.type is gtk.gdk.KEY_PRESS:
            sKeyName = gtk.gdk.keyval_name(oEvent.keyval)
            if sKeyName in ['Return','Escape']:
                if sKeyName == 'Escape':
                    self.set_selection(self._aOldSelection)
                self.__hide_list()
                return True # event handled
        return False # process further

    def fill_list(self, aVals):
        """Fill the list store with the given values"""
        self._oListStore.clear()
        for sEntry in aVals:
            oIter = self._oListStore.append(None)
            self._oListStore.set(oIter, 0, sEntry)

    def set_list_size(self, iW, iH):
        self._oDialog.set_size_request(iW, iH)

    def get_selection(self):
        """Return a list of the selected elements of the list"""
        aSelectedList = []
        oModel, oSelection = self._oTreeView.get_selection().get_selected_rows()
        for oPath in oSelection:
            oIter = oModel.get_iter(oPath)
            sName = oModel.get_value(oIter, 0)
            aSelectedList.append(sName)
        return aSelectedList

    def set_selection(self, aRowsToSelect):
        aRowsToSelect = set(aRowsToSelect)
        oIter = self._oListStore.get_iter_first()
        oTreeSelection = self._oTreeView.get_selection()
        oTreeSelection.unselect_all()
        while oIter is not None:
            sName = self._oListStore.get_value(oIter, 0)
            if sName in aRowsToSelect:
                oTreeSelection.select_iter(oIter)
            oIter = self._oListStore.iter_next(oIter)
