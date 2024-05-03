#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# preferred_setup.py
#
# This file contains functions that setup the sidebar and console window to my liking.
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  28-Apr-2024  1:46pm
# Modified :
#
# Copyright © 2024 By Gary Ash All rights reserved.
# ****************************************************************************************

import sublime
import sublime_plugin

firstTime = True


def plugin_loaded():
    global firstTime
    firstTime = True


def preferred_setup():
    activeWindow = sublime.active_window()
    if not activeWindow.is_sidebar_visible():
        activeWindow.set_sidebar_visible(True)

    if activeWindow.active_panel() is None:
        activeWindow.run_command("show_panel", {"panel": "console"})
        activeWindow.focus_group(activeWindow.active_group())


class PreferredSetupViewEventListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        global firstTime

        if firstTime or view.file_name() is not None:
            preferred_setup()
            firstTime = False

    def on_deactivated(self, view):
        preferred_setup()

    def on_close(self, view):
        preferred_setup()
