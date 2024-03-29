# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Menu for the CardSet View's
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details

"""Menu for the card set list"""

from gi.repository import Gtk
from .FilteredViewMenu import FilteredViewMenu
from .FrameProfileEditor import FrameProfileEditor
from .BaseConfigFile import CARDSET_LIST
from .MessageBus import MessageBus


class CardSetManagementMenu(FilteredViewMenu):
    """Card Set List Management menu.
       """
    # pylint: disable=too-many-public-methods
    # Gtk.Widget, so many public methods
    def __init__(self, oFrame, oWindow, oController):
        super().__init__(oFrame, oWindow, oController)
        self.__sName = 'Card Set List'
        self.__sSetTypeName = 'Card Set'
        self._oController = oController
        self._oCardSetProfileMenu = None
        self.__create_actions_menu()
        self.create_edit_menu()
        self.create_filter_menu()
        self.add_plugins_to_menus(self._oFrame)
        MessageBus.subscribe(MessageBus.Type.CONFIG_MSG,
                             'remove_profile', self.remove_profile)
        MessageBus.subscribe(MessageBus.Type.CONFIG_MSG,
                             'profile_option_changed',
                             self.profile_option_changed)

    # pylint: disable=attribute-defined-outside-init
    # called from __init__, so OK
    def __create_actions_menu(self):
        """Add the Actions Menu"""
        oMenu = self.create_submenu(self, "Actions")
        self.create_menu_item('Create New Card Set', oMenu,
                              self._oController.create_new_card_set)
        self.create_menu_item('Edit Card Set Properties', oMenu,
                              self._oController.edit_card_set_properties)
        self.create_menu_item('Mark/UnMark Card Set as in use', oMenu,
                              self._oController.toggle_in_use_flag)
        self.create_menu_item('Delete selected Card Set', oMenu,
                              self._oController.delete_card_set, 'Delete')
        oMenu.add(Gtk.SeparatorMenuItem())
        self.add_common_actions(oMenu)

    # pylint: enable=attribute-defined-outside-init

    def create_edit_menu(self):
        """Create the edit menu and populate it"""
        oMenu = self.create_submenu(self, "Edit")

        self.create_menu_item('Edit _Profiles', oMenu, self._edit_profiles)

        sProfile = self._oMainWindow.config_file.get_profile(CARDSET_LIST,
                                                             CARDSET_LIST)
        self._oCardSetProfileMenu = self._create_profile_menu(
            oMenu, "CardSet List Profile", CARDSET_LIST,
            self._select_cardset_list_profile, sProfile)

        self.add_edit_menu_actions(oMenu)

    def cleanup(self):
        """Remove the menu listener"""
        MessageBus.unsubscribe(MessageBus.Type.CONFIG_MSG, 'remove_profile',
                               self.remove_profile)
        MessageBus.unsubscribe(MessageBus.Type.CONFIG_MSG,
                               'profile_option_changed',
                               self.profile_option_changed)

    def _edit_profiles(self, _oWidget):
        """Open an options profiles editing dialog."""
        oDlg = FrameProfileEditor(self._oMainWindow,
                                  self._oMainWindow.config_file,
                                  CARDSET_LIST)
        sCurProfile = self._oMainWindow.config_file.get_profile(CARDSET_LIST,
                                                                CARDSET_LIST)
        oDlg.set_selected_profile(sCurProfile)
        oDlg.run()

        self._fix_profile_menu()

    def _fix_profile_menu(self):
        """Set the profile menu correctly"""
        sProfile = self._oMainWindow.config_file.get_profile(CARDSET_LIST,
                                                             CARDSET_LIST)
        self._update_profile_group(self._oCardSetProfileMenu, CARDSET_LIST,
                                   self._select_cardset_list_profile,
                                   sProfile)

    def _select_cardset_list_profile(self, oRadio, sProfileKey):
        """Callback to change the profile of the current card set."""
        if oRadio.get_active():
            oConfig = self._oMainWindow.config_file
            oConfig.set_profile(CARDSET_LIST, CARDSET_LIST, sProfileKey)

    # Respond to profile changes

    def remove_profile(self, _sSignal, sType, _sProfile):
        """A profile has been removed"""
        if sType == CARDSET_LIST:
            self._fix_profile_menu()

    def profile_option_changed(self, _sSignal, sType, _sProfile, sKey):
        """Update menu if profiles are renamed."""
        if sType == CARDSET_LIST and sKey == 'name':
            self._fix_profile_menu()
