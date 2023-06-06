from os import path as os_path
from pathlib import Path as pathlib_Path
from subprocess import PIPE, Popen
from typing import Any, Dict, Literal, Tuple, TypedDict, Union

import sublime
import sublime_plugin

PROJECT_NAME = "StyleLint-Formatter"
SETTINGS_FILE = f"{PROJECT_NAME}.sublime-settings"
PLATFORM = sublime.platform()
ARCHITECTURE = sublime.arch()
KEYMAP_FILE = f"Default ({PLATFORM}).sublime-keymap"
IS_WINDOWS = PLATFORM == "windows"
CODE_COMMAND_NOT_FOUND = 127


class SettingsData(TypedDict):
	variables: Dict[str, Any]
	config: Dict[str, Any]


class Settings:
	data: SettingsData = {
		"variables": {},
		"config": {},
	}

	@classmethod
	def set_settings(cls, view: sublime.View, variables: Dict[str, str]) -> None:
		settings_default = sublime.load_settings(SETTINGS_FILE).to_dict()
		settings_default = {k: v for k, v in Settings.flatten_dict(settings_default)}
		cls.data["config"] = settings_default

		settings_user = view.settings().to_dict()
		settings_user = {k: v for k, v in settings_user.items() if "StyleLint-Formatter" in k}
		settings_user = {k[20:]: v for k, v in Settings.flatten_dict(settings_user)}
		cls.data["config"].update(settings_user)

		variables.update({k: v for k, v in cls.data["config"].items() if "." not in k and isinstance(v, str)})
		cls.data["variables"] = variables

		for k, v in cls.data["config"].items():
			if isinstance(v, str) and "${" in v and "}" in v:
				v = sublime.expand_variables(v, cls.data["variables"])
				cls.data["config"][k] = v

			if isinstance(v, str) and "path" in k:
				v = os_path.normpath(os_path.expanduser(v))
				cls.data["config"][k] = v

	@classmethod
	def flatten_dict(cls, obj: Dict[str, Any], keystring: str = ""):
		if isinstance(obj, dict):
			keystring = f"{keystring}." if keystring else keystring

			for k in obj:
				yield from Settings.flatten_dict(obj[k], keystring + str(k))
		else:
			yield keystring, obj

	@classmethod
	def verify_settings(cls) -> None:
		node_path_exist: Union[Literal[True], Tuple[str, str]] = True
		stylelint_path_exist: Dict[Literal["local", "fallback"], Union[Literal[True], Tuple[str, str]]] = {
			"local": True,
			"fallback": True,
		}

		for k, v in cls.data["config"].items():
			if isinstance(v, str) and "node_" in k and "path" in k and PLATFORM.lower() in k:
				node_path_exist = True if os_path.exists(v) else (k, v)

			if isinstance(v, str) and "stylelint_" in k and "path" in k and PLATFORM.lower() in k:
				if "local" in k:
					stylelint_path_exist["local"] = True if os_path.exists(v) else (k, v)

				if "local" not in k:
					stylelint_path_exist["fallback"] = True if os_path.exists(v) else (k, v)

		if node_path_exist is not True:
			sublime.error_message("Node.js path does not exist. See console output.")
			raise Exception(f"\n>>> `node_path` does not exist: {node_path_exist[0]} -> {node_path_exist[1]}")

		if stylelint_path_exist["local"] is not True and stylelint_path_exist["fallback"] is not True:
			sublime.error_message("StyleLint path does not exist. See console output.")
			raise Exception(
				"\n>>> `local_stylelint_path` does not exist: "
				+ f"{stylelint_path_exist['local'][0]} -> {stylelint_path_exist['local'][1]}"
				+ "\n>>> `stylelint_path` does not exist: "
				+ f"{stylelint_path_exist['fallback'][0]} -> {stylelint_path_exist['fallback'][1]}"
			)

	@staticmethod
	def get_settings(view: Union[sublime.View, None]) -> SettingsData:
		variables = view.window().extract_variables()

		if view is not None and (
			variables["file_extension"] == "sublime-project"
			or len(Settings.data["variables"]) == 0
			or len(Settings.data["config"]) == 0
			or Settings.data["variables"]["file_extension"] != variables["file_extension"]
		):
			Settings.set_settings(view, variables)

		return Settings.data


class StyleLintFormatterEventListeners(sublime_plugin.EventListener):
	@staticmethod
	def should_run_command(view: sublime.View, settings: SettingsData) -> bool:
		extensions = settings["config"]["format_on_save_extensions"]
		extension = settings["variables"]["file_extension"] or settings["variables"]["file_name"].split(".")[-1]

		return not extensions or extension in extensions

	@staticmethod
	def on_pre_save(view: sublime.View) -> None:
		settings = Settings.get_settings(view)

		if settings["config"]["format_on_save"] and StyleLintFormatterEventListeners.should_run_command(view, settings):
			view.run_command("format_stylelint")

	# @staticmethod
	# def on_load(view: sublime.View) -> None:
	# """
	# // If using stylelint_d, set to `true` to stop the daemon when Sublime Text closes
	# // https://github.com/jo-sm/stylelint_d
	# // "using_stylelint_d": false,
	# """

	# 	## from contextlib import suppress as contextlib_suppress
	# 	## from subprocess import run as subprocess_run

	# 	settings = Settings.get_settings(view)

	# 	if settings["config"]["using_stylelint_d"] and (
	# 		"stylelint_d" in settings["config"]["local_stylelint_path"]
	# 		or (
	# 			"stylelint_d" not in settings["config"]["local_stylelint_path"]
	# 			and "stylelint_d" in settings["config"]["stylelint_path"]
	# 		)
	# 	):
	# 		cmd_node = settings["config"][f"node_path.{PLATFORM}".lower()]
	# 		cmd_stylelint = (
	# 			settings["config"][f"local_stylelint_path.{PLATFORM}".lower()]
	# 			or settings["config"][f"stylelint_path.{PLATFORM}".lower()]
	# 		)
	# 		with contextlib_suppress(Exception):
	# 			subprocess_run([cmd_node, cmd_stylelint, "start"])

	# @staticmethod
	# def on_exit() -> None:
	# """
	# // If using stylelint_d, set to `true` to stop the daemon when Sublime Text closes
	# // https://github.com/jo-sm/stylelint_d
	# // "using_stylelint_d": false,
	# """

	# 	## from contextlib import suppress as contextlib_suppress
	# 	## from os import kill as os_kill
	# 	## from signal import SIGKILL as signal_SIGKILL
	# 	## from subprocess import check_output as subprocess_check_output
	# 	## from subprocess import run as subprocess_run

	# 	settings = Settings.get_settings(None)

	# 	if settings["config"]["using_stylelint_d"] and (
	# 		"stylelint_d" in settings["config"]["local_stylelint_path"]
	# 		or (
	# 			"stylelint_d" not in settings["config"]["local_stylelint_path"]
	# 			and "stylelint_d" in settings["config"]["stylelint_path"]
	# 		)
	# 	):
	# 		cmd_node = settings["config"][f"node_path.{PLATFORM}".lower()]
	# 		cmd_stylelint = (
	# 			settings["config"][f"local_stylelint_path.{PLATFORM}".lower()]
	# 			or settings["config"][f"stylelint_path.{PLATFORM}".lower()]
	# 		)
	# 		with contextlib_suppress(Exception):
	# 			subprocess_run([cmd_node, cmd_stylelint, "stop"])
	# 			pids = map(int, subprocess_check_output(["pidof", "stylelint_d"]).split())

	# 			for pid in pids:
	# 				os_kill(int(pid), signal_SIGKILL)


class FormatStylelintCommand(sublime_plugin.TextCommand):
	def run(self, edit) -> None:
		settings = Settings.get_settings(self.view)

		if not StyleLintFormatterEventListeners.should_run_command(self.view, settings):
			print(">>> StyleLint-Formatter: File type not supported")
			return
		else:
			Settings.verify_settings()

		viewport_position = self.view.viewport_position()
		selections = list(self.view.sel())
		folded_regions = [self.view.substr(region) for region in self.view.folded_regions()]

		cmd_stylelint = [
			settings["config"][f"local_stylelint_path.{PLATFORM}".lower()]
			or settings["config"][f"stylelint_path.{PLATFORM}".lower()]
		]
		is_bin_cmd_stylelint = len(pathlib_Path(cmd_stylelint[0]).suffix) == 0
		cmd_node = [settings["config"][f"node_path.{PLATFORM}".lower()]] if not is_bin_cmd_stylelint else []
		cmd_config = ["--config", f"{settings['config']['config_path']}"] if settings["config"]["config_path"] else []
		cmd_extra = list(
			filter(
				lambda v: v
				not in {
					"-q",
					"--quiet",
					"--quiet-deprecation-warnings",
					"--rdd",
					"--report-descriptionless-disables",
					"--risd",
					"--report-invalid-scope-disables",
					"--rd",
					"--report-needless-disables",
				},
				settings["config"]["extra_args"],
			)
		) + (
			[
				"--report-descriptionless-disables",
				"--report-invalid-scope-disables",
				"--report-needless-disables",
				"--fix",
			]
			if settings["config"]["debug"]
			else ["--quiet", "--quiet-deprecation-warnings", "--fix"]
		)
		cmd_filename = ["--stdin", "--stdin-filename", f"{settings['variables']['file']}"]
		cmd = [v for v in (cmd_node + cmd_stylelint + cmd_config + cmd_extra + cmd_filename) if len(v)]

		buffer_region = sublime.Region(0, self.view.size())
		content = self.view.substr(buffer_region)
		content = content.encode("utf-8")

		try:
			p = Popen(
				cmd,
				stdout=PIPE,
				stdin=PIPE,
				stderr=PIPE,
				cwd=settings["variables"]["project_path"] or settings["variables"]["file_path"],
				shell=IS_WINDOWS,
			)
		except OSError:
			sublime.error_message("Couldn't find node.js. See console output.")
			raise Exception(
				"\n>>> Couldn't find node.js. Make sure it's in your $PATH by running `node --version` in your command-line."
			)

		stdout, stderr = p.communicate(input=content)
		stdout = stdout.decode("utf-8")
		stderr = stderr.decode("utf-8")

		if stderr and settings["config"]["debug"]:
			print(">>> StyleLint-Formatter:", " ".join(cmd))
			print(">>> Debug:", stderr)
		elif stderr:
			sublime.error_message(stderr)
			raise Exception(f"Error: {stderr}")
		elif p.returncode == CODE_COMMAND_NOT_FOUND:
			sublime.error_message(stderr or stdout)
			raise Exception(f"Error: {(stderr or stdout)}")
		elif stdout is None or len(stdout) < 1:
			return
		elif stdout != content:
			self.view.replace(edit, buffer_region, stdout)

			if not settings["config"]["debug"]:
				print(">>> StyleLint-Formatter (success):", " ".join(cmd))

		# Reapply code folds
		self.view.unfold(sublime.Region(0, len(stdout)))
		region_start = -1
		region_end = 0

		for region in folded_regions:
			try:
				region_start = stdout.find(region, region_end)
			finally:
				if region_start > -1:
					region_end = region_start + len(region)
					self.view.fold(sublime.Region(region_start, region_end))

		# Reapply viewport position
		self.view.set_viewport_position((0, 0), False)
		self.view.set_viewport_position(viewport_position, False)
		self.view.sel().clear()

		# Reapply cursor position and buffer selections
		for selection in selections:
			self.view.sel().add(selection)
