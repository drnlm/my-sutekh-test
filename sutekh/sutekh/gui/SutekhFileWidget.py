# SutekhFileWidget.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2008 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Provides base class for the file widgets and dialogs used in Sutekh -
# ensures set_name is called consistently, and updates the global working
# directory as appropriate

"""FileChooserWidget and FileChooserDialog wrapper for Sutekh"""

import gtk

def _changed_dir(oFileChooser, oParentWin):
    """Update parent's working dir when the folder changes."""
    oParentWin.set_working_dir(oFileChooser.get_current_folder())

class SutekhFileDialog(gtk.FileChooserDialog):
    # pylint: disable-msg=R0904
    # gtk widget, so has many public methods
    """Wrapper for the gtk.FileChooseDialog which updates the
       working dir of Sutekh."""

    def __init__(self, oParent, sTitle, oAction=gtk.FILE_CHOOSER_ACTION_OPEN,
            oButtons=None):
        super(SutekhFileDialog, self).__init__(sTitle, oParent, oAction,
                oButtons)
        self.set_name('Sutekh.dialog')
        sWorkingDir = oParent.get_working_dir()
        if sWorkingDir:
            self.set_current_folder(sWorkingDir)
        self.connect('current-folder-changed', _changed_dir, oParent)


class SutekhFileWidget(gtk.FileChooserWidget):
    # pylint: disable-msg=R0904
    # gtk widget, so has many public methods
    """Wrapper for the gtk.FileChooseWidget which updates the
       working dir of Sutekh."""
    def __init__(self, oParent, oAction=gtk.FILE_CHOOSER_ACTION_OPEN):
        super(SutekhFileWidget, self).__init__(oAction)
        sWorkingDir = oParent.get_working_dir()
        if sWorkingDir:
            self.set_current_folder(sWorkingDir)
        self.connect('current-folder-changed', _changed_dir, oParent)

class SutekhFileButton(gtk.FileChooserButton):
    # pylint: disable-msg=R0904
    # gtk widget, so has many public methods
    """Wrapper class for gtk.FileChooserButton which updates the
       working directory."""

    def __init__(self, oParent, sTitle):
        self.oDialog = SutekhFileDialog(oParent, sTitle,
                oButtons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        super(SutekhFileButton, self).__init__(self.oDialog)
        sWorkingDir = oParent.get_working_dir()
        if sWorkingDir:
            self.set_current_folder(sWorkingDir)
        self.oDialog.connect('map-event', self.mapped, oParent)

    # pylint: disable-msg=W0613
    # oWidget + oEvent needed by the function signature
    def mapped(self, oWidget, oEvent, oParent):
        """Update the dialogs working dir when the dialog is shown.

           We need this since the working dir will often change between
           button creation, and the dialog being popped up.
           """
        sWorkingDir = oParent.get_working_dir()
        if sWorkingDir:
            self.oDialog.set_current_folder(sWorkingDir)

class SimpleFileDialog(SutekhFileDialog):
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods
    """A simple file dialog, which just returns the file name"""
    def __init__(self, oParent, sTitle, oAction):
        super(SimpleFileDialog, self).__init__(oParent, sTitle,
                oAction, (gtk.STOCK_OK, gtk.RESPONSE_OK,
                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self.connect("response", self.button_response)
        self.set_local_only(True)
        self.set_select_multiple(False)
        self.sName = None

    # pylint: disable-msg=W0613
    # oWidget required by function signature
    def button_response(self, oWidget, iResponse):
        """Handle button press events"""
        if iResponse == gtk.RESPONSE_OK:
            self.sName = self.get_filename()
        self.destroy()

    def get_name(self):
        """Return the name to the caller."""
        return self.sName

class ImportDialog(SimpleFileDialog):
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods
    """Prompt the user for a file name to import"""
    def __init__(self, sTitle, oParent):
        super(ImportDialog, self).__init__(oParent, sTitle,
                gtk.FILE_CHOOSER_ACTION_OPEN)

class ExportDialog(SimpleFileDialog):
    # pylint: disable-msg=R0904
    # gtk.Widget, so many public methods
    """Prompt the user for a filename to export to"""
    def __init__(self, sTitle, oParent, sDefaultFileName=None):
        super(ExportDialog, self).__init__(oParent, sTitle,
                gtk.FILE_CHOOSER_ACTION_SAVE)
        self.set_do_overwrite_confirmation(True)
        if sDefaultFileName:
            self.set_current_name(sDefaultFileName)
