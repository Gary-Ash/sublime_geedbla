#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ****************************************************************************************
# edit-config-files.py
#
# This file contains commands to quickly configuration files for editing
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  27-Aug-2020  8:31pm
# Modified :  27-Aug-2020  8:31pm
#
# Copyright © 2020 By Gee Dbl A All rights reserved.
# ****************************************************************************************
import os
import sublime_plugin


class EditZshConfigFiles(sublime_plugin.WindowCommand):
    def run(self):
        zdotdir = os.getenv('ZDOTDIR', '')
        home = os.getenv('HOME', '')

        if zdotdir != '':
            zshrc = zdotdir + "/.zshrc"
            zshenv = zdotdir + "/.zshenv"
        else:
            zshrc = home + "/.zshrc"
            zshenv = home + "/.zshenv"

        bash_rc = home + "/.bashrc"
        bash_profile = home + "/.bash_profile"
        if os.path.exists(zshrc):
            self.window.open_file(zshrc)

        if os.path.exists(zshenv):
            self.window.open_file(zshenv)

        if os.path.exists(bash_rc):
            self.window.open_file(bash_rc)

        if os.path.exists(bash_profile):
            self.window.open_file(bash_profile)
