const path = require('path');
const ESLintPlugin = require('eslint-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const sass = require("sass");
const { watch } = require('fs');

module.exports = {
  entry: [
    './src/js/main.js',
    './src/html/index.html',
    './src/sass/main.scss',
    './src/html/favicon.ico'
  ],
  output: {
    filename: 'main.js',
    path: path.resolve(__dirname, 'dist'),
  },
  devServer: {
    static: {
      directory: "./dist",
      watch: true,
    },
    watchFiles: [
      './src/js/main.js',
      './src/html/index.html',
      './src/sass/main.scss'],
  },
  module: {
    rules: [
      {
        test: /\.html$/,
        type: "asset/source",
      },
      {
        test: /\.css$/,
        type: "asset/source",
      },
      {
        test: /\.ico$/,
        type: "asset/source",
      },
      {
          "test": /\.scss$/,
          "use": [
              MiniCssExtractPlugin.loader,
              {
                  "loader": "css-loader",
                  "options": {
                      "sourceMap": true
                  }
              },
              {
                  "loader": "sass-loader",
                  "options": {
                      "implementation": sass,
                      "sourceMap": true
                  }
              }
          ]
      },
      {
          "test": /\.css$/,
          "use": [MiniCssExtractPlugin.loader,
              "css-loader"
          ]
      },
    ]
  },
  mode: 'development',
  plugins: [
    new CopyPlugin({
        patterns: [
            { from: "./src/html/favicon.ico" },
            { from: "./src/html/index.html"},
        ]
    }),
    new ESLintPlugin({
        "context": ".",
        "extensions": ["js", "es6", "html"],
        "files": ["src", "test"],
        "exclude": ["dist/*", "**/*.min.js", "**/*.min.es6", "rollup.config.js"],
    }),
    new MiniCssExtractPlugin(),
  ],
};
