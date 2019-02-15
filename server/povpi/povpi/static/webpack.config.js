const webpack = require('webpack');
const path = require('path');

const config = {
  entry: __dirname + '/js/index.jsx',
  output: {
    path: __dirname + '/dist',
    filename: 'bundle.js'
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },
  module: {
    rules: [
      {
        enforce: 'pre',
        test: /\.jsx?/,
        exclude: /node_modules/,
        loader: 'eslint-loader',
        options: {
          eslintPath: path.join(__dirname, './node_modules/eslint'),
          fix: true
        }
      },
      {
        test: /\.jsx?/,
        exclude: /node_modules/,
        use: 'babel-loader'
      }
    ]
  }
};

module.exports = config;
