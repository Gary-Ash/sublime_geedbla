#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ****************************************************************************************
# preferred_setup.py
#
# This file contains functions that setup the sidebar and console window the way i likw it
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  27-Aug-2020  8:31pm
# Modified :   9-Jan-2021  7:48pm
#
# Copyright © 2020 By Gee Dbl A All rights reserved.
# ****************************************************************************************

import sublime
import sublime_plugin


def plugin_loaded():
    preferred_setup()


def preferred_setup():
    activeWindow = sublime.active_window()
    if not activeWindow.is_sidebar_visible():
        activeWindow.set_sidebar_visible(True)

    if activeWindow.active_panel() is None:
        activeWindow.run_command("show_panel", {"panel": "console"})
        activeWindow.focus_group(activeWindow.active_group())


class PreferredSetupViewEventListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        preferred_setup()

    def on_close(self, view):
        preferred_setup()

