#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# edit_config_files.py
#
# This file contains commands to quickly configuration files for editing
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  28-Feb-2025  6:44pm
# Modified :
#
# Copyright © 2024 By Gary Ash All rights reserved.
# ****************************************************************************************
import os
import sublime
import sublime_plugin
import sublime_geedbla.utilities


class EditConfigFiles(sublime_plugin.WindowCommand):
    def run(self):
        config = os.getenv("XDG_CONFIG_HOME", "")

        if os.path.exists(config):
            data = self.window.project_data()
            if data is not None:
                if "folders" in data:
                    folders = data["folders"]
                    folders.append({"path": config})
                    data["folders"] = folders
                else:
                    data = {"folders": [{"path": config}]}
            else:
                data = {"folders": [{"path": config}]}

            folders = data["folders"]
            for f in sublime_geedbla.utilities.folders_to_open:
                folders.append({"path": f})

            folders.append({"path": "~/.ssh"})
            data["folders"] = folders

            self.window.set_project_data(data)
        else:
            zdotdir = os.getenv("ZDOTDIR", "")
            home = os.getenv("HOME", "")
            kitty = os.getenv("HOME", "")
            kitty = kitty + "/.config/kitty/kitty.conf"

            if zdotdir != "":
                zprofile = zdotdir + "/.zprofile"
                zshrc = zdotdir + "/.zshrc"
                zshenv = zdotdir + "/.zshenv"
            else:
                zprofile = home + "/.zprofile"
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

                if os.path.exists(kitty):
                    self.window.open_file(kitty)

    def openFolder(folder):
        data = self.window.project_data()
        if data is not None:
            if "folders" in data:
                folders = data["folders"]
                folders.append({"path": folder})
                data["folders"] = folders
            else:
                data = {"folders": [{"path": folder}]}
        else:
            data = {"folders": [{"path": folder}]}

        self.window.set_project_data(data)
