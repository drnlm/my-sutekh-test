# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
# Copyright 2021 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Partly inspired by https://gist.github.com/brantfaircloth/764363

"""Test that plugins can be imported / support the correct versions"""

# This is not a functional test of any of the plugins as plugins can
# provide their own test classes for that, but aims to catch plugins
# that have not been updated to changes to the database schema and
# so forth. This is a simple 'counting fingers' sanity test

import unittest

from sutekh.tests.GuiSutekhTest import ConfigSutekhTest


from sutekh.base.gui.BasePluginManager import submodules
from sutekh.gui.PluginManager import PluginManager
import sutekh.gui.plugins as plugins



class TestPluginVersionImport(ConfigSutekhTest):
    """Class for testing version support for plugins.

       This is not a GuiSutekhTest, as we don't need all the plumbing"""

    def test_imports(self):

        aCandPlugins = sorted(submodules(plugins))
        aFailed = []
        aImported = []

        # pylint: disable=invalid-name
        # We use mPlugin to match the implementation
        for sPluginName in aCandPlugins:
            try:
                mPlugin = __import__("%s.%s" % (PluginManager.sPluginDir,
                                                sPluginName), None, None,
                                                [plugins])
                aImported.append((mPlugin, sPluginName))
            except Exception:
                aFailed.append(sPluginName)
                continue
        self.assertEqual(aFailed, [], "Failed import check")

        for mPlugin, sPluginName in aImported:
            if not hasattr(mPlugin, 'plugin'):
                continue
            cPlugin = mPlugin.plugin
            if not issubclass(cPlugin, PluginManager.cAppPlugin):
                continue
            if not cPlugin.check_versions():
                aFailed.append(sPluginName)
        self.assertEqual(aFailed, [], "Failed version check")
