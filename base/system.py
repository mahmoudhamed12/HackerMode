import os
import sys
import json
import marshal
import pathlib

from typing import List

sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-1]))


class System:
    TOOL_NAME: str = 'HackerMode'
    BASE_PATH: str = pathlib.Path(os.path.abspath(__file__)).parent

    def __init__(self):
        self.HACKERMODE_PACKAGES = self.HACKERMODE_PACKAGES()

    @property
    def HACKERMODE_ACTIVATE_FILE_PATH(self) -> str:
        """To get HackerMode activate file"""
        return os.path.join(self.TOOL_PATH, "HackerMode/bin/activate")

    @property
    def BASHRIC_FILE_PATH(self):
        if (shell := os.environ.get('SHELL')):
            if shell.endswith("bash"):
                path = os.path.join(shell.split("/bin/")[0], "etc/bash.bashrc")
                if not os.path.exists(path):
                    path = "/etc/bash.bashrc"
            elif shell.endswith("zsh"):
                path = os.path.join(shell.split("/bin/")[0], "etc/zsh/zshrc")
                if not os.path.exists(path):
                    path = "/etc/zsh/zshrc"
        return path

    @property
    def HACKERMODE_SHORTCUT(self) -> str:
        """HackerMode shortcut"""
        return f"\nalias HackerMode='source {self.HACKERMODE_ACTIVATE_FILE_PATH}'"

    @property
    def BIN_PATH(self) -> str:
        return ''.join(sys.executable.split('bin')[:-1]) + 'bin'

    @property
    def TOOL_PATH(self) -> str:
        '''To get the tool path'''
        ToolPath = os.path.join(os.environ['HOME'], '.HackerMode')
        if not os.path.isdir(ToolPath):
            os.mkdir(ToolPath)
        return ToolPath

    @property
    def PLATFORME(self) -> str:
        '''To get the platform name'''
        if sys.platform in ('win32', 'cygwin'):
            return 'win'

        elif sys.platform == 'darwin':
            return 'macosx'

        elif 'PWD' in os.environ and 'com.termux' in os.environ['PWD']:
            return 'termux'

        elif sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
            return 'linux'
        return 'unknown'

    @property
    def SYSTEM_PACKAGES(self) -> str:
        '''To gat all files that is in [/usr/bin] directory'''
        return os.listdir(self.BIN_PATH)

    def HACKERMODE_PACKAGES(self) -> List[str]:
        HackerModePackages = lambda path: [
            a for a in os.listdir(
                os.path.abspath(os.path.join(self.BASE_PATH, path)))
        ]
        packages: List[str] = []
        for file_name in HackerModePackages('bin'):
            for ext in ['.c', '.py', '.sh', '.dart', '.java', '.php', '.js', '.pyc', '.cpp']:
                if file_name.endswith(ext):
                    packages.append(file_name[0:-len(ext)])
        for tool_name in HackerModePackages('tools'):
            if tool_name not in packages:
                packages.append(tool_name)
        return list(set(packages))


System = System()
