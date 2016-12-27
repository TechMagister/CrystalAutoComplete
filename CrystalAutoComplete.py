import os
import sublime
import sublime_plugin
import re
import subprocess
import json
from subprocess import Popen, PIPE

settings = None


class Settings:
    def __init__(self):
        package_settings = sublime.load_settings("CrystalAutoComplete.sublime-settings")
        package_settings.add_on_change("cracker", settings_changed)
        package_settings.add_on_change("search_paths", settings_changed)

        self.cracker_bin = package_settings.get("cracker", "cracker")
        self.search_paths = package_settings.get("search_paths", [])
        self.package_settings = package_settings

    def unload(self):
        self.package_settings.clear_on_change("cracker")
        self.package_settings.clear_on_change("search_paths")


def plugin_loaded():
    global settings
    settings = Settings()


def plugin_unloaded():
    global settings
    if settings != None:
        settings.unload()
        settings = None


def settings_changed():
    global settings
    if settings != None:
        settings.unload()
        settings = None
    settings = Settings()


class Result:
    def __init__(self, parts):
        self.path = parts["path"]
        self.name = parts["name"]
        self.file = parts["file"]
        self.type = parts["type"]
        self.location = parts.get("location", "")
        self.signature = parts["signature"]


def run_cracker(view, loc):
    # Retrieve the entire buffer
    region = sublime.Region(0, loc)
    content = view.substr(region)

    cmd_list = []
    cmd_list.insert(0, settings.cracker_bin)
    cmd_list.append("client")
    cmd_list.append("--context")

    # Run cracker
    process = Popen(cmd_list, stdout=PIPE, stderr=PIPE, stdin=PIPE,
                    bufsize=1,
                    universal_newlines=True)

    (output, err) = process.communicate(input=content, timeout=2)

    exit_code = process.wait()

    # Parse results
    results = []
    if exit_code == 0:
        raw = json.loads(output)
        if raw["status"] == "success":
            raw_results = raw["results"]
            for r in raw_results:
                r["path"] = view.file_name()
                results.append(Result(r))
        pass
    else:
        print("CMD: '%s' failed: exit_code:" % ' '.join(cmd_list), exit_code, output, err)
    return results


class CrystalAutocomplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        # Check if this is a Crystal source file. This check
        # relies on the Crystal syntax formatting extension
        # being installed - https://github.com/crystal-lang/sublime-crystal
        if view.match_selector(locations[0], "source.crystal"):

            try:
                raw_results = run_cracker(view, locations[0])
            except FileNotFoundError:
                print("Unable to find cracker executable (check settings)")
                return

            results = []
            regexp = '[\.#](.+)\('

            for r in raw_results:
                if r.type == "Function":
                    if r.name.find("#") != -1:
                        trigger = r.name.split("#")[1]
                    else:
                        trigger = r.name.split(".")[1]
                    contents = trigger.split("(")[0]

                    if r.name.find("()") == -1:
                        contents = contents + '('
                else:
                    trigger = r.name
                    contents = r.name
                results.append([trigger, contents])

            if len(results) > 0:
                # return results
                return (results, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


#class CrystalGotoDefinitionCommand(sublime_plugin.TextCommand):
#    def run(self, edit):
#        # Get the buffer location in correct format for cracker
#        row, col = self.view.rowcol(self.view.sel()[0].begin())
#        row += 1
#
#        results = run_cracker(self.view, ["find-definition", str(row), str(col)])
#
#        if len(results) == 1:
#            result = results[0]
#            path = result.path
#            # On Windows the cracker will return the paths without the drive
#            # letter and we need the letter for the open_file to work.
#            if sublime.platform() == 'windows' and not re.compile('^\w\:').match(path):
#                path = 'c:' + path
#            encoded_path = "{0}:{1}:{2}".format(path, result.row, result.column)
#            self.view.window().open_file(encoded_path, sublime.ENCODED_POSITION)
