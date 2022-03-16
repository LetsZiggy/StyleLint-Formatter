# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import sublime, sublime_plugin
import platform
import glob
import os, sys, subprocess, codecs, webbrowser, signal, re
from subprocess import Popen, PIPE, check_output

try:
  import commands
except ImportError:
  pass

##########################################################################
##                                                                      ##
##             This project is inspired by and forked from              ##
##   ESLint-Formatter (https://github.com/TheSavior/ESLint-Formatter)   ##
##                  Based on: b76c47e on 22 May 2020                    ##
##                                                                      ##
##########################################################################

PROJECT_NAME = "StyleLint-Formatter"
SETTINGS_FILE = PROJECT_NAME + ".sublime-settings"
KEYMAP_FILE = "Default ($PLATFORM).sublime-keymap"

IS_WINDOWS = platform.system() == "Windows"


class FormatStylelintCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    # Save the current viewport position to scroll to it after formatting.
    previous_selection = list(self.view.sel())  # Copy.
    previous_position = self.view.viewport_position()

    # Save the already folded code to refold it after formatting.
    # Backup of folded code is taken instead of regions because the start and end pos
    # of folded regions will change once formatted.
    folded_regions_content = [self.view.substr(r) for r in self.view.folded_regions()]

    # Get the current text in the buffer and save it in a temporary file.
    # This allows for scratch buffers and dirty files to be linted as well.
    entire_buffer_region = sublime.Region(0, self.view.size())

    buffer_text = self.get_buffer_text(entire_buffer_region)

    output = self.run_script_on_file(filename=self.view.file_name(), content=buffer_text)

    # log output in debug mode
    if PluginUtils.get_pref(["debug"], self.view):
      print(output)

    # If the prettified text length is nil, the current syntax isn't supported.
    if output == None or len(output) < 1:
      return

    # Replace the text only if it's different.
    if output != buffer_text:
      self.view.replace(edit, entire_buffer_region, output)

    self.refold_folded_regions(folded_regions_content, output)
    self.view.set_viewport_position((0, 0), False)
    self.view.set_viewport_position(previous_position, False)
    self.view.sel().clear()

    # Restore the previous selection if formatting wasn't performed only for it.
    # if not is_formatting_selection_only:
    for region in previous_selection:
      self.view.sel().add(region)

  def get_buffer_text(self, region):
    buffer_text = self.view.substr(region)
    return buffer_text

  def get_lint_directory(self, filename):
    project_path = PluginUtils.project_path(None)
    if project_path is not None:
      return PluginUtils.normalize_path(project_path)
    if filename is not None:
      cdir = os.path.dirname(filename)
      if os.path.exists(cdir):
        return cdir
    return os.getcwd()

  def run_script_on_file(self, filename=None, content=None):
    try:
      dirname = filename and os.path.dirname(filename)
      node_path = PluginUtils.get_node_path(self.view)
      stylelint_path = PluginUtils.get_stylelint_path(dirname, self.view)

      if stylelint_path == False:
        sublime.error_message("stylelint could not be found on your path")
        return

      if filename is None:
        sublime.error_message("Cannot lint unsaved file")

      # Better support globally-available stylelint binaries that don't need to be invoked with node.
      node_cmd = [node_path] if node_path else []
      cmd = node_cmd + [stylelint_path, "--fix", "--stdin", "--stdin-filename", filename]

      project_path = PluginUtils.project_path()
      extra_args = PluginUtils.get_pref(["extra_args"], self.view)
      if extra_args:
        cmd += [arg.replace("$project_path", project_path) for arg in extra_args]

      if PluginUtils.get_pref(["debug"], self.view):
        print("stylelint command line", cmd)

      config_path = PluginUtils.get_pref(["config_path"], self.view)

      if os.path.isfile(config_path):
        # If config file path exists, use as is
        full_config_path = config_path
      else:
        # Find config file relative to project path
        full_config_path = os.path.join(project_path, config_path)

      if os.path.isfile(full_config_path):
        print("Using configuration from {0}".format(full_config_path))
        cmd.extend(["--config", full_config_path])

      cdir = self.get_lint_directory(filename)

      if type(content) == str:
        content = content.encode("utf-8")

      output = PluginUtils.get_output(cmd, cdir, content)
      output = re.sub("\n+$", "\n", output)

      return output

    except:
      # Something bad happened.
      msg = str(sys.exc_info()[1])
      print("Unexpected error({0}): {1}".format(sys.exc_info()[0], msg))
      sublime.error_message(msg)

  def refold_folded_regions(self, folded_regions_content, entire_file_contents):
    self.view.unfold(sublime.Region(0, len(entire_file_contents)))
    region_end = 0

    for content in folded_regions_content:
      region_start = entire_file_contents.index(content, region_end)
      if region_start > -1:
        region_end = region_start + len(content)
        self.view.fold(sublime.Region(region_start, region_end))


class StyleLintFormatterEventListeners(sublime_plugin.EventListener):
  @staticmethod
  def should_run_command(view):
    if not PluginUtils.get_pref(["format_on_save"], view):
      return False

    extensions = PluginUtils.get_pref(["format_on_save_extensions"], view)
    extension = os.path.splitext(view.file_name())[1][1:]

    # Default to using filename if no extension
    if not extension:
      extension = os.path.basename(view.file_name())

    # Skip if extension is not listed
    return not extensions or extension in extensions

  @staticmethod
  def on_pre_save(view):
    if StyleLintFormatterEventListeners.should_run_command(view):
      view.run_command("format_stylelint")

  @staticmethod
  def on_exit():
    try:
      pids = map(int, check_output(["pidof", "stylelint_d"]).split())
      for pid in pids:
        os.kill(int(pid), signal.SIGKILL)
    except:
      pass


class PluginUtils:
  @staticmethod
  # Fetches root path of open project
  def project_path(fallback=os.getcwd()):
    project_data = sublime.active_window().project_data()

    # if cannot find project data, use cwd
    if project_data is None:
      return fallback

    folders = project_data["folders"]
    folder_path = folders[0]["path"]
    return folder_path

  @staticmethod
  def get_pref(key_list, view=None):
    if view is not None:
      settings = view.settings()

      # Flat settings in .sublime-project
      flat_keys = ".".join(key_list)
      if settings.has(f"{PROJECT_NAME}.{flat_keys}"):
        value = settings.get(f"{PROJECT_NAME}.{flat_keys}")
        return value

      # Nested settings in .sublime-project
      if settings.has(PROJECT_NAME):
        value = settings.get(PROJECT_NAME)

        for key in key_list:
          try:
            value = value[key]
          except:
            value = None
            break

        if value is not None:
          return value

    global_settings = sublime.load_settings(SETTINGS_FILE)
    value = global_settings.get(key_list[0])

    # Load active project settings
    project_settings = sublime.active_window().active_view().settings()

    # Overwrite global config value if it's defined
    if project_settings.has(PROJECT_NAME):
      value = project_settings.get(PROJECT_NAME).get(key_list[0], value)

    return value

  @staticmethod
  def get_node_path(view=None):
    platform = sublime.platform()

    # .sublime-project
    node = PluginUtils.get_pref(["node_path", platform], view)

    # .sublime-settings
    node = node.get(platform) if isinstance(node, dict) else node

    if type(node) == str:
      print("Using node.js path on '" + platform + "': " + node)
    else:
      print("Not using explicit node.js path")
    return node

  # Convert path that possibly contains a user tilde and/or is a relative path into an absolute path.
  @staticmethod
  def normalize_path(path, realpath=False):
    if realpath:
      return os.path.realpath(os.path.expanduser(path))
    else:
      project_dir = sublime.active_window().project_file_name()
      if project_dir:
        cwd = os.path.dirname(project_dir)
      else:
        cwd = os.getcwd()
      return os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))

  # Yield path and every directory above path.
  @staticmethod
  def walk_up(path):
    curr_path = path
    while 1:
      yield curr_path
      curr_path, tail = os.path.split(curr_path)
      if not tail:
        break

  # Find the first path matching a given pattern within dirname or the nearest ancestor of dirname.
  @staticmethod
  def findup(pattern, dirname=None):
    if dirname is None:
      project_path = PluginUtils.project_path()
      normdn = PluginUtils.normalize_path(project_path)
    else:
      normdn = PluginUtils.normalize_path(dirname)

    for d in PluginUtils.walk_up(normdn):
      matches = glob.glob(os.path.join(d, pattern))
      if matches:
        return matches[0]

    return None

  @staticmethod
  def get_local_stylelint(dirname, view=None):
    pkg = PluginUtils.findup("node_modules/stylelint", dirname)
    if pkg == None:
      return None
    else:
      platform = sublime.platform()

      # .sublime-project
      path = PluginUtils.get_pref(["local_stylelint_path", platform], view)

      # .sublime-settings
      path = path.get(platform) if isinstance(path, dict) else path

      if not path:
        return None
      d = os.path.dirname(os.path.dirname(pkg))
      local_stylelint_path = os.path.join(d, path)

      if os.path.isfile(local_stylelint_path):
        return local_stylelint_path
      else:
        return None

  @staticmethod
  def get_stylelint_path(dirname, view=None):
    platform = sublime.platform()
    stylelint = dirname and PluginUtils.get_local_stylelint(dirname, view)

    # if local stylelint not available, then using the settings config
    if stylelint is None:
      # .sublime-project
      stylelint = PluginUtils.get_pref(["stylelint_path", platform], view)

      # .sublime-settings
      stylelint = stylelint.get(platform) if isinstance(stylelint, dict) else stylelint

    print("Using stylelint path on '" + platform + "': " + stylelint)
    return stylelint

  @staticmethod
  def get_output(cmd, cdir, data):
    try:
      p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=cdir, shell=IS_WINDOWS)
    except OSError:
      raise Exception("Couldn't find Node.js. Make sure it's in your $PATH by running `node -v` in your command-line.")
    stdout, stderr = p.communicate(input=data)
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    if stderr:
      raise Exception("Error: %s" % stderr)
    elif p.returncode == 127:
      raise Exception("Error: %s" % (stderr or stdout))
    else:
      return stdout
