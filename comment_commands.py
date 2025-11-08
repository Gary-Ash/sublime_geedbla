#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# comment_commands.py
#
# This file contains the implementation of comment building commands
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  28-Feb-2025  6:44pm
# Modified :
#
# Copyright © 2024 By Gary Ash All rights reserved.
# ****************************************************************************************

import re
import os
import datetime
import sublime
import sublime_plugin
import sublime_geedbla.utilities
import sublime_geedbla.preferred_setup
from pathlib import Path

fileHeader = """top_line
inner_line FILENAME_PLACEHOLDER
inner_line
inner_line
inner_line
inner_line Author   :  AUTHOR_PLACEHOLDER <EMAIL_PLACEHOLDER>
inner_line Created  :  TIMESTAMP_PLACEHOLDER
inner_line Modified :
inner_line
inner_line Copyright © YEAR_PLACEHOLDER By ORGANIZATION_PLACEHOLDER All rights reserved.
last_line """


def plugin_loaded():
    loadTemplateFile()
    sublime_geedbla.utilities.load_aettings()


def loadTemplateFile():
    global fileHeader

    fileHeaderTemplateFile = (
        sublime.packages_path() + "/User/sublime_geedbla_file_header.txt"
    )
    chk_file = Path(fileHeaderTemplateFile)
    if chk_file.is_file():
        fileHandle = open(fileHeaderTemplateFile, "r")
        fileHeader = fileHandle.read()
    else:
        fileHandle = open(fileHeaderTemplateFile, "w")
        fileHeader = fileHandle.write(fileHeader)

    fileHandle.close()


def buildFileHeader(view, do_value_replacement=True):
    global fileHeader

    shebangs = {
        "Perl": "perl",
        "Python": "python3",
        "Ruby": "ruby",
        "Awk": "awk",
        "AppleScript": "osascript",
        "AppleScript (Binary)": "osascript",
    }

    (row, column) = sublime_geedbla.utilities.get_cursor_position(view)
    (comment_start, comment_end) = sublime_geedbla.utilities.get_comment(view)

    single_line_comment = comment_start
    if len(comment_end) > 0:
        top_line = comment_start.ljust(
            sublime_geedbla.utilities.line_length - column, "*"
        )
        inner_line = " *"
        last_line = " " + comment_end.rjust(
            sublime_geedbla.utilities.line_length - 1 - column, "*"
        )
    else:
        top_line = single_line_comment.ljust(
            sublime_geedbla.utilities.line_length - column, "*"
        )
        inner_line = comment_start.strip()
        last_line = single_line_comment.ljust(
            sublime_geedbla.utilities.line_length - column, "*"
        )

    now = datetime.datetime.now()
    timestamp = now.strftime("%_d-%b-%Y  %_I:%M%p")
    timestamp = timestamp.replace("AM", "am")
    timestamp = timestamp.replace("PM", "pm")
    year = str(now.year)
    filename = view.file_name()
    if filename is None:
        filename = "<Untitled-File>"

    the_shell = os.environ["SHELL"]
    syn = sublime_geedbla.utilities.get_syntax(view)
    if len(the_shell) > 0:
        shebangs["Bash"] = os.path.basename(the_shell)
    else:
        shebangs["Bash"] = "bash"

    if syn in shebangs:
        landing_line = 3
        header = "#!/usr/bin/env " + shebangs[syn] + "\n"
        if syn == "Python" or syn == "Ruby":
            landing_line = 4
            header += "# -*- coding: utf-8 -*-\n"
    else:
        landing_line = 2
        header = ""

    header += fileHeader

    comment_replacement = {
        "top_line": top_line,
        "inner_line": inner_line,
        "last_line": last_line,
    }

    value_replacements = {
        "FILENAME_PLACEHOLDER": os.path.basename(filename),
        "YEAR_PLACEHOLDER": year,
        "TIMESTAMP_PLACEHOLDER": timestamp,
        "AUTHOR_PLACEHOLDER": sublime_geedbla.utilities.author,
        "EMAIL_PLACEHOLDER": sublime_geedbla.utilities.email_address,
        "ORGANIZATION_PLACEHOLDER": sublime_geedbla.utilities.organization,
        "___ORGANIZATIONNAME___": sublime_geedbla.utilities.organization,
    }

    for key in comment_replacement:
        header = header.replace(key, comment_replacement[key])

    if do_value_replacement:
        for key in value_replacements:
            header = header.replace(key, value_replacements[key])

    return (landing_line, header)


class EditFileHeaderTemplate(sublime_plugin.WindowCommand):
    def run(self):
        fileHeaderTemplateFile = (
            sublime.packages_path() + "/User/sublime_geedbla_file_header.txt"
        )
        if os.path.exists(fileHeaderTemplateFile):
            self.window.open_file(fileHeaderTemplateFile)


class CommentCommandsEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        fileHeaderTemplateFile = (
            sublime.packages_path() + "/User/sublime_geedbla_file_header.txt"
        )
        filename = view.file_name()
        if filename == fileHeaderTemplateFile:
            loadTemplateFile()


class UpdateCommentHeaderCommand(sublime_plugin.TextCommand):
    rCopyright = sublime.Region(-1, -1)
    hdr = []
    now = datetime.datetime.now()

    def isOneOfMyFiles(self):
        # --------------------------------------------------------------------------------
        # Check for a copyright notice for my or my organization to determine if i should
        # do anything at all
        # --------------------------------------------------------------------------------
        self.rCopyright = self.view.find(
            "\x43opyright © .* By .* All rights reserved.", 0
        )
        if self.rCopyright.empty() or "comment" not in self.view.scope_name(
            self.rCopyright.a
        ):
            return False

        copyrightStr = self.view.substr(self.rCopyright)

        foundOrg = False
        if sublime_geedbla.utilities.organizations is not None:
            for org in sublime_geedbla.utilities.organizations:
                if org in copyrightStr:
                    foundOrg = True
                    sublime_geedbla.utilities.organization = org
                    break

        if foundOrg is False:
            if "___ORGANIZATIONNAME___" not in copyrightStr:
                return False
        return True

    def updateCopyrightNotice(self, edit):
        # --------------------------------------------------------------------------------
        # update the Copyright notice
        # --------------------------------------------------------------------------------
        self.now = datetime.datetime.now()
        year_region = self.view.find("20[0-9]*", self.rCopyright.a)
        last_year = self.view.substr(year_region)

        if int(last_year) < self.now.year:
            s = "Copyright © %s-%d By %s All rights reserved." % (
                last_year,
                datetime.datetime.now().year,
                sublime_geedbla.utilities.organization,
            )
        else:
            s = "Copyright © %s By %s All rights reserved." % (
                last_year,
                sublime_geedbla.utilities.organization,
            )
        self.view.replace(edit, self.rCopyright, s)

    def updateFileName(self, edit):
        # --------------------------------------------------------------------------------
        # set or update the file name if there is one
        # --------------------------------------------------------------------------------
        nf = self.view.file_name()
        if nf is not None:
            new_file_name = os.path.basename(nf)
            r = self.view.find("<Untitled-File>", 0)
            if not r.empty() and "comment" in self.view.scope_name(r.a):
                self.view.replace(edit, r, new_file_name)
            else:
                new_file_name_location = re.search(new_file_name, self.hdr)
                if new_file_name_location is not None:
                    file_name_search = self.hdr[0 : new_file_name_location.start() - 1]
                    r = self.view.find(file_name_search, 0, sublime.LITERAL)
                    if not r.empty() and "comment" in self.view.scope_name(r.a):
                        file_name_region = self.view.line(r)
                        r.a = r.b + 1
                        r.b = file_name_region.b
                        self.view.replace(edit, r, new_file_name)

    def updateDateStamps(self, edit):
        # --------------------------------------------------------------------------------
        # update the file creation time stamp
        # --------------------------------------------------------------------------------
        r = self.view.find("\x43reated.*:.*$", 0)
        if not r.empty() and "comment" in self.view.scope_name(r.a):
            r2 = self.view.find(":.*", r.a)
            if not r2.empty() and "comment" in self.view.scope_name(r.a):
                r2.a = r2.a + 1
                dateStr = self.view.substr(r2)
                if "/" in dateStr:
                    timestamp = created.strftime("Created  :  %_e-%b-%Y %_I:%M%p")
                    timestamp = timestamp.replace("AM", "am")
                    timestamp = timestamp.replace("PM", "pm")
                    self.view.replace(edit, r, timestamp)
        # --------------------------------------------------------------------------------
        # update the file modification time stamp
        # --------------------------------------------------------------------------------
        r = self.view.find("\x4Dodified.*:.*$", 0)
        if not r.empty() and "comment" in self.view.scope_name(r.a):
            timestamp = self.now.strftime("Modified :  %_e-%b-%Y %_I:%M%p")
            timestamp = timestamp.replace("AM", "am")
            timestamp = timestamp.replace("PM", "pm")
            self.view.replace(edit, r, timestamp)

    def updateAuthorship(self, edit):
        # --------------------------------------------------------------------------------
        # update authorship
        # --------------------------------------------------------------------------------
        r = self.view.find("(.*)(Programmer|Author)(.*:)(.*)", 0)
        if not r.empty() and "comment" in self.view.scope_name(r.a):
            original_author_line_region = self.view.line(r)
            (author_row, _) = self.view.rowcol(original_author_line_region.a)
            original_author_line = self.view.substr(original_author_line_region)
            new_author_location = re.search(
                "(.*)(Programmer|Author)(.*:)(.*)", self.hdr
            )
            if new_author_location is not None:
                new_author_line = self.hdr[
                    new_author_location.start() : new_author_location.end()
                ]
                matches = re.match(
                    r"(.*(Programmer|Author)(.*:\s*))([A-z0-9]*\s*[A-z0-9]*)\s*(<[A-z0-9.]*@[A-z0-9.]*>)",
                    original_author_line,
                )
                author_name = matches.group(4)
                author_email = matches.group(5)
                if (
                    author_name == sublime_geedbla.utilities.author
                    and author_email != sublime_geedbla.utilities.email_address
                ):
                    self.view.replace(
                        edit, original_author_line_region, new_author_line
                    )
                    return

                if author_name != sublime_geedbla.utilities.author:
                    if "Author" in original_author_line:
                        new_author_search = original_author_line.replace(
                            "Author", "      "
                        )
                    if "Programmer" in original_author_line:
                        new_author_search = original_author_line.replace(
                            "Programmer", "          "
                        )

                    r = self.view.find(new_author_search, 0, sublime.LITERAL)
                    if r.empty():
                        author_comment = new_author_line + "\n" + new_author_search
                        self.view.replace(
                            edit, original_author_line_region, author_comment
                        )
            else:
                self.view.erase(edit, original_author_line_region)

    def run(self, edit):
        if not self.isOneOfMyFiles():
            return

        self.updateCopyrightNotice(edit)
        (_, self.hdr) = buildFileHeader(self.view)

        self.updateFileName(edit)
        self.updateDateStamps(edit)
        self.updateAuthorship(edit)


class SeperatorLineCommentCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.view = self.window.active_view()
        self.window.show_input_panel(
            "Enter a decorator character: ", "", None, self.on_change, None
        )

    def on_change(self, decorator):
        self.window.run_command("hide_panel", {"cancel": True})
        self.insert_seperator(decorator)
        sublime_geedbla.preferred_setup.preferred_setup()

    def insert_seperator(self, decorator):
        if len(decorator) == 0:
            return

        decorator = decorator[0]

        (_, column) = sublime_geedbla.utilities.get_cursor_position(self.view)
        (comment_start, comment_end) = sublime_geedbla.utilities.get_comment(self.view)
        if sublime_geedbla.utilities.get_syntax(self.view) == "PHP":
            comment_end = ""
            comment_start = "#"

        sepLine = (
            comment_start.ljust(
                sublime_geedbla.utilities.line_length - len(comment_end) - column,
                decorator,
            )
            + comment_end
            + "\n"
        )
        self.view.run_command("insert", {"characters": sepLine})


class BoxCommentCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.view = self.window.active_view()
        self.window.show_input_panel(
            "Enter a decorator character: ", "", None, self.on_change, None
        )

    def on_change(self, decorator):
        self.window.run_command("hide_panel", {"cancel": True})
        self.insertbox(decorator)
        sublime_geedbla.preferred_setup.preferred_setup()

    def insertbox(self, decorator):
        if len(decorator) == 0:
            return

        decorator = decorator[0]
        (row, column) = sublime_geedbla.utilities.get_cursor_position(self.view)
        (comment_start, comment_end) = sublime_geedbla.utilities.get_comment(self.view)

        if sublime_geedbla.utilities.get_syntax(self.view) == "PHP":
            comment_end = ""
            comment_start = "#"

        if len(comment_end) > 0:
            first = (
                comment_start.ljust(
                    sublime_geedbla.utilities.line_length - column, decorator
                )
                + "\n"
            )
            second = " * \n"
            third = " *" + comment_end.rjust(
                sublime_geedbla.utilities.line_length - column - 2, decorator
            )
        else:
            first = (
                comment_start.ljust(
                    sublime_geedbla.utilities.line_length - column, decorator
                )
                + "\n"
            )
            second = comment_start.strip() + " \n"
            third = comment_start.ljust(
                sublime_geedbla.utilities.line_length - column, decorator
            )

        self.view.run_command("insert", {"characters": first})
        self.view.run_command("insert", {"characters": second})
        sublime_geedbla.utilities.set_cursor_position(self.view, row + 2, column)

        self.view.run_command("insert", {"characters": third})

        sublime_geedbla.utilities.set_cursor_position(self.view, row + 1, 0)
        self.view.run_command("move_to", {"to": "eol"})


class HeaderCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        (landing_line, header) = buildFileHeader(self.view)
        r = sublime.Region(0, 4)
        if "comment" in self.view.scope_name(r.a):
            self.view.run_command("update_comment_header")
            sublime_geedbla.utilities.set_cursor_position(self.view, landing_line, 3)
            r = self.view.find("\S", self.view.sel()[0].a)
            r.b -= 1
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(r.b, r.b))
        else:
            self.view.insert(edit, 0, header)
            sublime_geedbla.utilities.set_cursor_position(self.view, landing_line, 3)
            self.view.run_command("move_to", {"to": "eol"})
            self.view.run_command("insert", {"characters": " "})


class CommentEventListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command("update_comment_header")
