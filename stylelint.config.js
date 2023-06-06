/* eslint-disable unicorn/no-null */

const rootRules = {
	"at-rule-no-unknown": [true, { ignoreAtRules: ["apply", "layer", "responsive", "screen", "tailwind", "variants"] }],

	"no-unknown-animations": true,

	"at-rule-no-vendor-prefix": true,

	"declaration-no-important": true,

	"media-feature-name-no-vendor-prefix": true,

	"property-no-vendor-prefix": true,

	"selector-no-vendor-prefix": true,

	"value-no-vendor-prefix": true,

	"value-keyword-case": "lower",

	"at-rule-empty-line-before": ["always", { except: ["blockless-after-blockless", "first-nested"], ignoreAtRules: ["apply", "layer", "responsive", "screen", "tailwind", "variants"] }],

	"declaration-empty-line-before": "never",

	"font-weight-notation": ["numeric", { ignore: ["relative"] }],

	"font-family-name-quotes": "always-unless-keyword",

	"function-url-quotes": ["always", { except: ["empty"] }],

	"selector-attribute-quotes": "always",

	"shorthand-property-no-redundant-values": true,

	// ---csstree-validator--- //

	// "csstree/validator": {
	// 	ignoreAtrules: ["apply", "layer", "responsive", "screen", "tailwind", "variants"],
	// },
}

/** @type {import("stylelint").Config} */
export default {
	"extends": ["stylelint-config-standard", "stylelint-config-recess-order"],
	"plugins": ["stylelint-order"],
	"processors": [],
	"ignoreFiles": [
		"**/.git",
		"**/.svn",
		"**/.hg",
		"**/CVS",
		"**/node_modules",
		"**/vendor",
		"**/.env",
		"**/.venv",
		"**/env",
		"**/venv",
		"**/ENV",
		"**/env.bak",
		"**/venv.bak",
		"**/__pycache__",
	],
	"rules": rootRules,
	"overrides": [
		{
			files: ["**/*.html"],
			rules: {
				"no-missing-end-of-source-newline": null,
			},
		},
	],
}
