#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# utilities.py
#
# This file is a collection of small utility functions
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  28-Feb-2025  6:44pm
# Modified :
#
# Copyright © 2024 By Gary Ash All rights reserved.
# ****************************************************************************************
import os
import sublime
from pathlib import Path


def plugin_loaded():
    settingsFile = sublime.packages_path() + "/User/sublime_geedbla.sublime-settings"
    chk_file = Path(settingsFile)
    if not chk_file.is_file():
        settings = sublime.load_settings("sublime_geedbla.sublime-settings")
        settings.set("line_length", 90)
        settings.set("author", "")
        settings.set("email", "")
        settings.set("organizations", [])
        settings.set("folders_to_open", [])
        sublime.save_settings("sublime_geedbla.sublime-settings")

    load_aettings()
    settings = sublime.load_settings("sublime_geedbla.sublime-settings")
    settings.add_on_change("sublime_geedbla.sublime-settings", lambda: load_aettings())


def load_aettings():
    global author
    global email_address
    global organizations
    global line_length
    global organization
    global organizations
    global folders_to_open

    settings = sublime.load_settings("sublime_geedbla.sublime-settings")

    line_length = settings.get("line_length", 90)
    author = settings.get("author", "Gary Ash")
    email_address = settings.get("email", "gary.ash@icloud.com")
    organizations = settings.get("organizations", ["Gee Dbl A"])
    folders_to_open = settings.get("folders_to_open", ["/opt/geedbla"])

    try:
        organization = organizations[0]
    except:
        organization = "Gee Dbl A"


def plugin_unloaded():
    settings = sublime.load_settings("sublime_geedbla.sublime-settings")
    settings.clear_on_change("sublime_geedbla.sublime-settings")


def get_syntax(view):
    syn = view.settings().get("syntax")
    syn = os.path.basename(syn)
    syn = syn.split(".")[0]
    return syn


def get_comment(view):
    comment_start = ""
    comment_end = ""
    comment_number = ""
    comments_only = {}

    comment_exception = {
        "Ruby": ("#", ""),
        "Python": ("# ", ""),
        "AppleScript": ("(*", "*)"),
        "AppleScript (Binary)": ("(*", "*)"),
    }

    language = get_syntax(view)
    if language in comment_exception:
        return comment_exception[language]

    shell_variables = view.meta_info("shellVariables", 0)
    for variable_dic in shell_variables:
        name = variable_dic["name"]
        if "TM_COMMENT_" in name:
            comments_only[name] = variable_dic["value"]

    for i in range(1, 4):
        if i > 1:
            comment_number = "_" + str(i)

        start_name = "TM_COMMENT_START" + comment_number
        end_name = "TM_COMMENT_END" + comment_number

        if start_name in comments_only:
            comment_start = comments_only[start_name].strip()
        if end_name in comments_only:
            comment_end = comments_only[end_name].strip()
            break

    return (comment_start, comment_end)


def get_cursor_position(view):
    cursor = view.sel()[0]
    (row, _) = view.rowcol(cursor.begin())
    cur_x = view.text_to_layout(cursor.b)[0]

    line = view.substr(view.line(cursor))
    if line:
        line_length = len(line)
        stripped_line_length = len(line.lstrip())

        if stripped_line_length > 0:
            beginning_pos = line_length - stripped_line_length
            beginning_point = view.text_point(row, beginning_pos)
            cur_x = view.text_to_layout(beginning_point)[0]

    column = int(cur_x / view.em_width())
    return (row, column)


def set_cursor_position(view, row, col):
    pt = view.text_point(row, col)
    view.sel().clear()
    view.sel().add(sublime.Region(pt))
    view.show(pt)
