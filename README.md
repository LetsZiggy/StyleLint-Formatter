# StyleLint-Formatter for Sublime Text

*Please note the plugin hasn't been submitted to [packagecontrol.io](https://packagecontrol.io/). Thus has to be installed manually.*

<br>

### Installation

#### Prerequisites

- `stylelint` is installed either locally or globally ([Link](https://www.npmjs.com/package/stylelint))
- `stylelint.config.js` has been configured ([Link](https://stylelint.io/user-guide/configure))

#### Installing Plugin

- `Package Control: Add Repository` Method (Recommended)
	1. Open `Command Palette` (Default: `ctrl+shift+p`)
	2. ``Package Control: Add Repository``
	3. `https://raw.githubusercontent.com/LetsZiggy/StyleLint-Formatter/main/repository-package.json`
	4. Open `Command Palette`
	5. `Package Control: Install Package`
	6. `StyleLint-Formatter`
- "Manual" Method (Requires manual update)
	1. Download this repository through `Download ZIP`
	2. Rename folder to `StyleLint-Formatter`
	3. Move folder to `[SublimeText]/Packages` folder
		- To access `[SublimeText]/Packages` folder:
			1. Open/Restart `Sublime Text`
			2. Open the `Command Palette` (Default: `ctrl+shift+p`)
			3. `Preferences: Browse Packages`
	4. Restart `Sublime Text`

---

### Commands

#### Command palette:

- `StyleLint Formatter: Format this file`

#### Shortcut key:

* Linux/Windows: `Ctrl + Shift + ;`
* Mac: `Cmd + Shift + ;`

---

### Usage

#### Using Default Settings ({ format_on_save: false })

1. Save current changes
	- Formatting will only be applied to the saved file and _**not the current buffer**_
2. Use one of the available commands to run StyleLint-Formatter

---

### Configuring Settings

#### To access and modify settings file

Go to `Preferences -> Package Settings -> StyleLint-Formatter -> Settings`

#### To override settings per project basis

To override global plugin configuration for a specific project, add a settings object with a `StyleLint-Formatter` key in your `.sublime-project`. This file is accessible via `Project -> Edit Project`.

```javascript
/* EXAMPLE */
{
	"folders": [
		{
			"path": ".",
		},
	],
	"settings": {
		"StyleLint-Formatter": {
			"format_on_save": true,
		},
	},
}
```

#### Default settings

```javascript
{
	/**
	 * Simply using `node` without specifying a path sometimes doesn't work :(
	 * If these are false, we'll invoke the stylelint binary directly.
	 * https://github.com/victorporof/Sublime-HTMLPrettify#oh-noez-command-not-found
	 * http://nodejs.org/#download
	 */
	"node_path": {
		"windows": "node.exe",
		"linux": "/usr/bin/nodejs",
		"osx": "/usr/local/bin/node",
	},

	/**
	 * The location to search for a locally installed stylelint package
	 * These are all relative paths to a project's directory
	 * If this is not found or are false, it will try to fallback to a global package
	 * (see "stylelint_path" below)
	 */
	"local_stylelint_path": {
		"windows": "${project_path}/node_modules/stylelint/bin/stylelint.js",
		"linux": "${project_path}/node_modules/.bin/stylelint",
		"osx": "${project_path}/node_modules/.bin/stylelint",
	},

	/**
	 * The location of the user/global installed stylelint package to use as a fallback
	 */
	"stylelint_path": {
		"windows": "%APPDATA%/npm/node_modules/stylelint/bin/stylelint",
		"linux": "/usr/bin/stylelint",
		"osx": "/usr/local/bin/stylelint",
	},

	/**
	 * Specify this path to an stylelint config file to override the default behavior
	 * Passed to stylelint as --config. Read more here:
	 * 	- https://stylelint.io/user-guide/configuration
	 * If an absolute path is provided, it will use as is.
	 * Else, it will look for the file in the root of the project directory.
	 * Failing either, it will skip the config file
	 */
	"config_path": "",

	/**
	 * Pass additional arguments to stylelint.
	 * Read more here: https://stylelint.io/user-guide/cli
	 * Please note that "-q | --quiet | --quiet-deprecation-warnings | --report-descriptionless-disables | --rdd | --report-invalid-scope-disables | --risd | --report-needless-disables | --rd" in `extra_args` will be filtered out (see `debug` below)
	 */
	"extra_args": [],

	/**
	 * Automatically format when a file is saved
	 */
	"format_on_save": false,

	/**
	 * Only attempt to format files with whitelisted extensions on save.
	 * Leave empty to disable the check
	 */
	"format_on_save_extensions": [
		"css",
		"sass",
		"scss",
		"less",
		"styl",
	],

	/**
	 * Logs stylelint output messages to console when set to true
	 * Options below will be added to `extra_args` based on `debug` value:
	 * 	- false:
	 * 		- "--quiet" will be added
	 * 		- "--quiet-deprecation-warnings" will be added
	 * 		- "--report-descriptionless-disables | --rdd" will be removed
	 * 		- "--report-invalid-scope-disables | --risd" will be removed
	 * 		- "--report-needless-disables | --rd" will be removed
	 * 	- true:
	 * 		- "-q | --quiet" will be removed
	 * 		- "--quiet-deprecation-warnings" will be removed
	 * 		- "--report-descriptionless-disables" will be added
	 * 		- "--report-invalid-scope-disables" will be added
	 * 		- "--report-needless-disables" will be added
	 */
	"debug": false,
}
```

This project is inspired by and forked from [ESLint-Formatter](https://github.com/TheSavior/ESLint-Formatter).
