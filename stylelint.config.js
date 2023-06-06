/** @type {import("stylelint").Config} */
export default {
	"extends": ["stylelint-config-standard", "stylelint-config-recess-order"],
	"plugins": ["stylelint-order"],
	"processors": [],
	"ignoreFiles": [
		"**/.git/",
		"**/.svn/",
		"**/.hg/",
		"**/CVS/",
		"**/node_modules/",
		"**/vendor/",
		"**/.env/",
		"**/env/",
		"**/.venv/",
		"**/venv/",
		"**/.env.bak/",
		"**/env.bak/",
		"**/.venv.bak/",
		"**/venv.bak/",
		"**/ENV/",
		"**/__pycache__/",
	],
}
