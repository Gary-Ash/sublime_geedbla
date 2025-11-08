#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ****************************************************************************************
# execution_bit.py
#
# This Sublime Text event listener will set Unix executable bit on a file appears to have
# the start of a Unix she-bang "#!/" as ib #!/usr/bash, #!/usr/bin/env python, etc
#
# Author   :  Gary Ash <gary.ash@icloud.com>
# Created  :  28-Feb-2025  6:44pm
# Modified :
#
# Copyright © 2024 By Gary Ash All rights reserved.
# ****************************************************************************************
import os
import stat
import sublime_plugin


class ExecutionBitEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        ignoreList = [
            ".profile",
            ".bash_profile",
            ".bash_logout",
            ".bashrc",
            ".zshrc",
            ".zshenv",
            ".zlogin",
            ".zlogout",
        ]

        filename = view.file_name()
        if filename != "":
            baseName = os.path.basename(filename)
            if baseName not in ignoreList:
                r = view.find("#!/", 0)
                c = view.find("#compdef", 0)
                if not r.empty() or not c.empty():
                    perm = os.stat(filename).st_mode & 0o777
                    os.chmod(view.file_name(), perm | stat.S_IRWXU)
