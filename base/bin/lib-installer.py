#!/usr/bin/python
import re
import os
import sys
import json
import base64
import requests
import subprocess
from threading import Thread

from pip._internal.utils.misc import site_packages
from pip._internal.commands import create_command

from bs4 import BeautifulSoup as Soup

from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress, BarColumn

DESCRIPTION = b'Clt5ZWxsb3ddZnJvbVtyZWRdOlsvcmVkXVsveWVsbG93XQogICAgW2JsdWVdQHBzaC10ZWFtWy9ibHVlXSBbY3lhbl0jIEhhY2tlck1vZGVbL2N5YW5dClt5ZWxsb3ddZXhhbXBsZVtyZWRdOlsvcmVkXVsveWVsbG93XQogICAgW3JlZF0kWy9yZWRdIFtncmVlbl1saWItaW5zdGFsbGVyWy9ncmVlbl0gW2JsdWVdc2VhcmNoWy9ibHVlXSBbbGlnaHRfc2FsbW9uM11ubWFwWy9saWdodF9zYWxtb24zXQogICAgW3JlZF0kWy9yZWRdIFtncmVlbl1saWItaW5zdGFsbGVyWy9ncmVlbl0gW2JsdWVdaW5mb1svYmx1ZV0gW2xpZ2h0X3NhbG1vbjNdcmVxdWVzdHNbL2xpZ2h0X3NhbG1vbjNdCiAgICBbcmVkXSRbL3JlZF0gW2dyZWVuXWxpYi1pbnN0YWxsZXJbL2dyZWVuXSBbYmx1ZV1pbnN0YWxsWy9ibHVlXSBbbGlnaHRfc2FsbW9uM11ubWFwWy9saWdodF9zYWxtb24zXQoKW3llbGxvd11zZWFyY2hbcmVkXTpbL3JlZF1bL3llbGxvd10KICAgIFtjeWFuXVNlYXJjaCBmcm9tIHB5cGkub3JnIGluIGxpYnJhcnlbL2N5YW5dCiAgICBbYmx1ZV1zZWFyY2ggW3JlZF08Wy9yZWRdW2xpZ2h0X3NhbG1vbjNdbGlicmFyeS1uYW1lWy9saWdodF9zYWxtb24zXVtyZWRdPlsvcmVkXQpbeWVsbG93XWluZm9bcmVkXTpbL3JlZF1bL3llbGxvd10KICAgIFtjeWFuXWdldCBhbGwgaW5mb3JtYXRpb24gZnJvbSBsaWJyYXJ5Wy9jeWFuXQogICAgW2JsdWVdaW5mbyBbcmVkXTxbL3JlZF1bbGlnaHRfc2FsbW9uM11saWJyYXJ5LW5hbWVbL2xpZ2h0X3NhbG1vbjNdW3JlZF0+Wy9yZWRdClt5ZWxsb3ddaW5zdGFsbFtyZWRdOlsvcmVkXVsveWVsbG93XQogICAgW2N5YW5daW5zdGFsbCBMaWJyYXJ5IVsvY3lhbl0KICAgIFtibHVlXWluc3RhbGwgW3JlZF08Wy9yZWRdW2xpZ2h0X3NhbG1vbjNdbGlicmFyeS1uYW1lWy9saWdodF9zYWxtb24zXVtyZWRdPlsvcmVkXQo='

console = Console()

class LibInstaller:
    
    def __init__(self):
        self.pypi = "https://pypi.org"
        self.console = Console
    
    
    def exists(self, libname: str) ->bool:
        return os.path.exists(os.path.join(site_packages, libname))
    
    def _popen(self, command: str) -> str:
        PIPE = subprocess.PIPE
        return subprocess.Popen(
            command,
            stdout=PIPE,
            stdin=PIPE,
            stderr=PIPE,
            shell=True,
        ).communicate()[0].decode()

    def _info_lib_as_json(self, libname: str) -> dict:
        lines: list = self._popen(f'pip show {libname}').split('\n')
        data: dict = {}
        for line in lines:
            if line:
                find = re.findall("([\w\W\S]*):\ (.*)", line)
                if find:
                    data[find[0][0]] = find[0][1]
        if not data:
            data = {
                "Error": "No Library found",
                "try-open": f"{self.pypi}/pypi/{libname}/json",
                "try-search": f"{self.pypi}/search/?q={libname.replace(' ', '+')}"
            }
        return data
        
    def _panel(self, description: str, title: str, **kwargs) -> None:
        expand = kwargs.get('expand')
        if expand != None:
            kwargs.pop('expand')
        else:
            expand = True
        console.print(
            Panel(
                description,
                expand=expand,
                title=title,
                **kwargs
            )
        )
    
    def info(self, libname: str) -> None:
        lib_info = self._info_lib_as_json(libname)
        _name = lib_info.get('Name')
        _version = lib_info.get("Version")
        title = ("[white]" + _name if _name else "[red]None") + (" [green]" + _version if _version else "")
        description = json.dumps({f'[blue]{k}[/blue]': v for k, v in lib_info.items()}, indent=3,).replace('"', '')
        self._panel(
            description,
            title,
            border_style="cyan",
        )
        
    
    def install(self, libname: str):
       
        with Progress(BarColumn(), console=console) as progres:
            progres.add_task("", total=100, start=False)
            if self.exists(libname):
                console.print("[yellow]# library is Exists![/yellow]")
            isdone = create_command("install").main([libname]) == 0
        if isdone or self.exists(libname):
            console.print("[blue]# Done[/blue]")
        else:
            console.print("[red]# ERROR[/red]")
    
    def search(self, name: str) -> None:
        with Progress(BarColumn(), console=console) as progres:
            progres.add_task("", total=100, start=False)
            table = self.__search(name)
        console.print(table) 
    
    
    def __search(self, name: str) -> Table:
        page = 1
        lib = 0
        table = Table(
            title="Search for Library",
            expand=False,
            caption_justify="right",
        )
        table.add_column("Name", style="cyan", header_style="bright_cyan")
        table.add_column("Version", style="blue", header_style="bright_blue")
        table.add_column("Command", style="yellow", header_style="bright_yellow")
        while True:
                req = requests.get(f"{self.pypi}/search/", {"q": name, "page": page})
                if req.status_code == 200:
                    console.print(f"[yellow]from:[/yellow] {req.url}")
                    soup = Soup(req.content, "html.parser")
                    for a in soup.find_all("a", {"class": "package-snippet"}):
                        _name = a.find("span", {"class": "package-snippet__name"})
                        version = a.find("span", {"class": "package-snippet__version"})
                        
                        version = version.text if version else "None"
                        _name = _name.text if _name else "None"
                        table.add_row(
                            _name,
                            version,
                            f"pip[black]_[/black]install[black]_[/black]{_name}=={version}"  if name + version != "NoneNone" else "None",
                            style="dim" if self.exists(_name) else "none"
                        )
                        lib += 1
                else:
                    break
                if page > 3: # Change
                    break
                page += 1
        table.caption = f"{lib} progects for '{name}'."
        return table



if __name__ == "__main__":
    argv = sys.argv[1:]
    lib_installer = LibInstaller()
    help_msg = lambda: lib_installer._panel(base64.b64decode(DESCRIPTION).decode(), "[white]lib[red]-[/red]installer", expand=False, border_style="cyan")
    if len(argv) >= 2:
        try:
            lib_installer.__getattribute__(argv[0])(argv[1])
        except AttributeError:
            help_msg()
        except Exception as e:
            print(f"# {e.__class__.__name__}: {str(e)}")
            help_msg()
    else:
        help_msg()
        
    

