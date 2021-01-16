#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# run_formatter.py
#
# This file contains utility functions that will run a program/formatting on the contents
# of the current buffer or selected text there in
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  27-Aug-2020  8:31pm
# Modified :  20-Oct-2020  3:05pm
#
# Copyright © 2020 By Gee Dbl A All rights reserved.
# ****************************************************************************************
import sublime
import sublime_plugin
import subprocess
from .utilities import *


class UniversalFormatSource(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        command = self.pick_formatter(self.view)
        if not command:
            sublime.status_message("No formatter defined for this language.")
            return

        selections = self.view.sel()
        cursor = self.view.sel()[0]

        if selections[0].empty():
            region = sublime.Region(0, self.view.size())
            self.view.sel().clear()
            self.view.sel().add(region)

        for selection in selections:
            if not selection.empty():
                source_code = self.view.substr(selection).encode("utf-8")
                try:
                    proc = subprocess.Popen(command,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

                    (formatted, errors) = proc.communicate(input=source_code)
                    formatter_return = proc.poll()
                    if formatter_return == 0:
                        self.view.replace(edit, selection, formatted.decode("utf-8"))
                    else:
                        error_message = "The formatter returned an error code of %x : %s" % (formatter_return, errors)
                        sublime.error_message(error_message)

                except Exception as ex:
                    error_message = "The formatter returned an error message %s" % (ex)
                    sublime.error_message(error_message)

                self.view.sel().clear()
                self.view.sel().add(cursor)
                sublime.status_message("Formatting complete.")

    def is_enabled(self):
        ret = False
        current_lang = get_syntax(self.view)
        supported_languages = ["C", "C++", "C#", "Objective-C", "Objective-C++", "Java", "Go", "Perl", "Python", "Swift", "Ruby"]
        if current_lang in supported_languages:
            ret = True
        return ret

    def pick_formatter(self, view):
        command = []
        language = get_syntax(view)
        settings = sublime.load_settings("sublime_geedbla.sublime-settings")

        if (language == "C" or language == "C++" or language == "C#" or language == "Java" or language == "Objective-C" or language == "Objective-C++"):
            uncrustify_languages = {
                "C": "C",
                "C++": "CPP",
                "C#": "CS",
                "Java": "Java",
                "Objective-C": "OC",
                "Objective-C++": "OC++",
            }
            formatter_exec = settings.get("uncrustify exec", "/usr/local/bin/uncrustify")
            cfg_file = settings.get("uncrustify config", "-c /Users/garyash/.config/.uncrustify")
            cfg_list = cfg_file.split()
            command = [formatter_exec, "-l", uncrustify_languages[language]]
            command.extend(cfg_list)
            return command
        elif (language == "Perl"):
            formatter_exec = settings.get("perltidy exec", "/usr/local/bin/perltidy")
            cfg_file = settings.get("perltidy config", "-pro=/Users/garyash/.config/.perltidyrc -st")
            cfg_list = cfg_file.split()
            command = ["perl", formatter_exec]
            command.extend(cfg_list)
            return command
        elif (language == "Swift"):
            formatter_exec = settings.get("swiftformat exec", "/usr/local/bin/swiftformat")
            cfg_file = settings.get("swiftformat config", "--config /Users/garyash/.config/.swiftformat")
            cfg_list = cfg_file.split()
            command = [formatter_exec]
            command.extend(cfg_list)
            return command
        elif (language == "Go"):
            cfg_file = settings.get("go config", "")
            command = [settings.get("go exec", "/usr/local/bin/gofmt"), cfg_file]
            return command
        elif (language == "Python"):
            command = [settings.get("python exec", "/usr/local/bin/black")]
            cfg_file = settings.get("python config", "--config /Users/garyash/.config/.black -")
            cfg_list = cfg_file.split()
            command.extend(cfg_list)
            return command
        elif (language == "Ruby"):
            command = [settings.get("ruby exec", "rbprettier")]
            cfg_file = settings.get("ruby config", "")
            cfg_list = cfg_file.split()
            command.extend(cfg_list)
            return command
