# FullBackup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2007 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details
"""Plugin to wrap zipfile backup and restore methods"""

from sutekh.gui.PluginManager import CardListPlugin
from sutekh.gui.SutekhDialog import do_complaint_error, do_complaint_warning
from sutekh.gui.SutekhFileWidget import SutekhFileDialog
from sutekh.gui.ProgressDialog import ProgressDialog, SutekhCountLogHandler
from sutekh.io.ZipFileWrapper import ZipFileWrapper
import gtk
import os

class FullBackup(CardListPlugin):
    """"
    Provide access to ZipFileWrapper's backup and restore methods.
    Handle GUI aspects associated with restoring (ensuring everything
    reloads, etc.)
    """

    dTableVersions = {}
    aModelsSupported = ["MainWindow"]

    # Dialog and Menu Item Creation

    def get_menu_item(self):
        """Register on the Plugins menu"""
        if not self.check_versions() or not self.check_model_type():
            return None

        oMenuItem = gtk.MenuItem("Backup")
        oMenu = gtk.Menu()
        oMenuItem.set_submenu(oMenu)

        oBackup = gtk.MenuItem("Save a Full Backup")
        oBackup.connect("activate", self.activate_backup)
        oRestore = gtk.MenuItem("Restore a Full Backup")
        oRestore.connect("activate", self.activate_restore)

        oMenu.add(oBackup)
        oMenu.add(oRestore)

        return ('Plugins', oMenuItem)

    # Menu responses

    # pylint: disable-msg=W0613
    # oWidget needed by gtk function signature
    def activate_backup(self, oWidget):
        """Handle backup request"""
        oDlg = self.make_backup_dialog()
        oDlg.run()

    # oWidget needed by gtk function signature
    def activate_restore(self, oWidget):
        """Handle restore request"""
        oDlg = self.make_restore_dialog()
        oDlg.run()
    # pylint: enable-msg=W0613

    # Backup

    def make_backup_dialog(self):
        """Create file dialog for backup"""
        sName = "Choose a file to save the full backup to ..."

        oDlg = SutekhFileDialog(self.parent, sName,
                oAction=gtk.FILE_CHOOSER_ACTION_SAVE,
                oButtons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        oDlg.set_name("Sutekh.dialog")

        oDlg.connect("response", self.handle_backup_response)
        oDlg.set_local_only(True)
        oDlg.set_select_multiple(False)
        oDlg.show_all()

        return oDlg

    # pylint: disable-msg=R0201
    # This could be a function, but that won't add any clarity to this code
    def handle_backup_response(self, oDlg, oResponse):
        """Handle response from backup dialog"""
        if oResponse == gtk.RESPONSE_OK:
            sFile = oDlg.get_filename()
            bContinue = True

            if os.path.exists(sFile):
                bContinue = do_complaint_warning("Overwrite existing file %s?"
                        % sFile) != gtk.RESPONSE_CANCEL

            if bContinue:
                try:
                    oLogHandler = SutekhCountLogHandler()
                    oProgressDialog = ProgressDialog()
                    oProgressDialog.set_description("Saving backup")
                    oLogHandler.set_dialog(oProgressDialog)
                    oProgressDialog.show()
                    oFile = ZipFileWrapper(sFile)
                    oFile.do_dump_all_to_zip(oLogHandler)
                    oProgressDialog.destroy()
                # pylint: disable-msg=W0703
                # we really do want all the exceptions
                except Exception, oException:
                    sMsg = "Failed to write backup.\n\n" + str(oException)
                    do_complaint_error(sMsg)

        oDlg.destroy()
    # pylint: enable-msg=R0201

    # Restore

    def make_restore_dialog(self):
        """Create file chooser dialog for restore"""
        sName = "Restore a Full Backup ...."

        oDlg = SutekhFileDialog(self.parent, sName,
                oAction=gtk.FILE_CHOOSER_ACTION_OPEN,
                oButtons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        oDlg.set_name("Sutekh.dialog")

        oWarning = gtk.Label("This will delete all existing Physical Cards"
                " and Card Sets")
        # pylint: disable-msg=E1101
        # plint doesn't pick up vbox methods correctly
        oDlg.vbox.pack_start(oWarning, expand=False)
        oDlg.vbox.reorder_child(oWarning, 0)
        oDlg.connect("response", self.handle_restore_response)
        oDlg.set_local_only(True)
        oDlg.set_select_multiple(False)
        oDlg.show_all()

        return oDlg

    def handle_restore_response(self, oDlg, oResponse):
        """Handle response from the restore dialog"""
        if oResponse == gtk.RESPONSE_OK:
            sFile = oDlg.get_filename()
            bContinue = True

            if not os.path.exists(sFile):
                bContinue = do_complaint_warning(
                        "Backup file %s does not seem to exist."
                        % sFile) != gtk.RESPONSE_CANCEL

            if bContinue:
                try:
                    aEditable = self.parent.get_editable_panes()
                    oLogHandler = SutekhCountLogHandler()
                    oProgressDialog = ProgressDialog()
                    oProgressDialog.set_description("Restoring backup")
                    oLogHandler.set_dialog(oProgressDialog)
                    oProgressDialog.show()
                    oFile = ZipFileWrapper(sFile)
                    oFile.do_restore_from_zip(self.cardlookup, oLogHandler)
                    # restore successful, refresh display
                    self.reload_all()
                    oProgressDialog.destroy()
                    self.parent.restore_editable_panes(aEditable)
                # pylint: disable-msg=W0703
                # we really do want all the exceptions
                except Exception, oException:
                    sMsg = "Failed to restore backup.\n\n" + str(oException)
                    do_complaint_error(sMsg)

        oDlg.destroy()

# pylint: disable-msg=C0103
# accept plugin name
plugin = FullBackup
