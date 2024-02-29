#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# new_from_selection.py
#
# This file contains the implementation of a command that will create a new buffer/file
# containing the selected text of the current buffer
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  27-Aug-2020  8:31pm
# Modified :  27-Aug-2020  8:31pm
#
# Copyright © 2020 By Gee Dbl A All rights reserved.
# ****************************************************************************************
import sublime_plugin


class NewFromSelection(sublime_plugin.TextCommand):
    def run(self, edit):
        output_view = self.view.window().new_file()
        for region in self.view.sel():
            output_view.insert(edit, 0, self.view.substr(region))

    def is_enabled(self):
        return not self.view.sel()[0].empty()
