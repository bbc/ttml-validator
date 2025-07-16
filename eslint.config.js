// import { defineConfig } from "eslint/config";
const { defineConfig } = require("eslint/config");

module.exports = defineConfig([
// export default [
    {
        files: [ 
            "**/*.js",
            "**/*.es6",
            "**/*.mjs",
            // "**/*.html",
            // "index.html",
        ],
        ignores: [
            "dist/*",
            "node_modules/*",
            "**/*.min.js",
            "**/*.min.es6",
            "rollup.config.js",
            "eslint.config.js",
            "libs/*",
        ],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
        },
        rules: {
            "no-empty-label": 0,
            "no-labels": 1,
            
            "no-arrow-condition": 0,
            "no-confusing-arrow": 2,
            "no-constant-condition": 2,

            "space-after-keywords": 0,
            "space-before-keywords": 0,
            "space-return-throw-case": 0,
            "keyword-spacing": 2,

            "filenames/filenames": 0,

            "no-console": 1,
            "no-magic-numbers": 0,
            "consistent-this": 0,
            "prefer-template": 0,
            "max-len": ["warn", {code:160, "ignoreStrings": true}],

            "max-params": ["error", 6],

            "no-console": "off",

            // "max-statements": ["error", 30]

        },

    }
]);
