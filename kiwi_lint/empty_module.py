# Copyright (c) 2018 Alexander Todorov <atodorov@MrSenko.com>

# Licensed under the GPL 2.0: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import os

from pylint import interfaces
from pylint import checkers
from pylint.checkers import utils


class EmptyModuleChecker(checkers.BaseChecker):
    __implements__ = (interfaces.IAstroidChecker,)

    name = 'empty-module-checker'

    msgs = {'E4481': ("Remove empty module from git!",
                      'remove-empty-module',
                      "Kiwi TCMS doesn't need to carry around modules which are empty. "
                      "They must be removed from the source code!")}

    @utils.check_messages('remove-empty-module')
    def visit_module(self, node):
        if not node.body and not node.path[0].endswith('__init__.py'):
            self.add_message('remove-empty-module', node=node)


class ModuleInDirectoryWithoutInitChecker(checkers.BaseChecker):
    __implements__ = (interfaces.IAstroidChecker,)

    name = 'dir-without-init-checker'

    msgs = {'R4482': ("Python module found in directory without __init__.py",
                      'module-in-directory-without-init',
                      "Python module is found inside a directory which is "
                      "missing __init__.py! This will lead to missing packages when "
                      "tarball is built for distribution on PyPI! See "
                      "https://github.com/kiwitcms/Kiwi/issues/790")}

    # this works against tcms/ directory and will not take into account
    # if we want to examine only a sub-dir or a few files
    # all files found by os.walk
    all_python_files = set()
    # all modules found by pylint, which conveniently skips files/dirs
    # with missing __init__.py
    discovered_python_files = set()

    def open(self):
        project_root = os.path.join(os.path.dirname(__file__), '..', 'tcms')
        project_root = os.path.abspath(project_root)

        for root, dirs, files in os.walk(project_root, topdown=False):
            # skip migrations
            if root.find('migrations') > -1:
                continue

            for file_name in files:
                if file_name.endswith('.py'):
                    self.all_python_files.add(
                        os.path.join(project_root, root, file_name))

    def visit_module(self, node):
        for file_name in node.path:
            self.discovered_python_files.add(file_name)

    @utils.check_messages('module-in-directory-without-init')
    def close(self):
        # todo: refactor to keep a reference to module nodes
        # and pass them to add_message() with a C/E message
        diff = self.all_python_files - self.discovered_python_files
        diff = list(diff)
        diff.sort()

        if diff:
            self.add_message('module-in-directory-without-init')
            for m in diff:
                print(m)
