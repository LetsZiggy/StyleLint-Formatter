# StyleLint-Formatter for Sublime Text

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

#### Default settings:

```javascript
{
  // Simply using `node` without specifying a path sometimes doesn't work :(
  // If these are false, we'll invoke the stylelint binary directly.
  // https://github.com/victorporof/Sublime-HTMLPrettify#oh-noez-command-not-found
  // http://nodejs.org/#download
  "node_path": {
    "windows": "node.exe",
    "linux": "/usr/bin/nodejs",
    "osx": "/usr/local/bin/node",
  },

  // The location to search for a locally installed stylelint package
  // These are all relative paths to a project's directory
  // If this is not found or are false, it will try to fallback to a global package
  // (see "stylelint_path" below)
  "local_stylelint_path": {
    "windows": "node_modules/stylelint/bin/stylelint.js",
    "linux": "node_modules/.bin/stylelint",
    "osx": "node_modules/.bin/stylelint",
  },

  // The location of the globally installed stylelint package to use as a fallback
  "stylelint_path": {
    "windows": "%APPDATA%/npm/node_modules/stylelint/bin/stylelint",
    "linux": "/usr/bin/stylelint",
    "osx": "/usr/local/bin/stylelint",
  },

  // Specify this path to an stylelint config file to override the default behavior
  // Passed to stylelint as --config. Read more here:
  // https://stylelint.io/user-guide/configuration
  // If an absolute path is provided, it will use as is.
  // Else, it will look for the file in the root of the project directory.
  // Failing either, it will skip the config file
  "config_path": "",

  // Pass additional arguments to stylelint.
  //
  // Each command should be a string where it supports the following replacements:
  //   $project_path - The path to the projects root folder
  //
  // Example:
  //   ["--parser-options={\"tsconfigRootDir\": \"$project_path\"}"]
  "extra_args": [],

  // Automatically format when a file is saved
  "format_on_save": false,

  // Only attempt to format files with whitelisted extensions on save.
  // Leave empty to disable the check
  "format_on_save_extensions": [
    "css",
    "sass",
    "scss",
    "less",
    "styl",
  ],

  // Logs stylelint output messages to console when set to true
  "debug": false,
}
```

---

### Performance

If you experience performance issues, it may be worth taking a look at [`stylelint_d`](https://www.npmjs.com/package/stylelint_d). You can modify the settings to point to the `stylelint_d` binary instead of `stylelint`.

```javascript
/* EXAMPLE */
{
  "local_stylelint_path": {
    "windows": "node_modules/stylelint/bin/stylelint_d.js",
    "linux": "node_modules/.bin/stylelint_d",
    "osx": "node_modules/.bin/stylelint_d",
  },
}
```

---

This project is inspired by and forked from [ESLint-Formatter](https://github.com/TheSavior/ESLint-Formatter).
