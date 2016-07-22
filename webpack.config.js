var webpack = require('webpack');
var path = require('path');

module.exports = {
  entry: './assets/js/index.js',
  output: {
    path: './trulii/static',
    filename: 'bundle.js',
    libraryTarget: "umd"
  },
  module: {
    loaders: [
      { test: /\.css$/, loader: "style!css" },
      { test: /\.sass$/, loader: "style!css!sass" },
      { test: /\.svg$/, loader: "svg-url-loader" }
    ]
  },
  plugins: [
    new webpack.ProvidePlugin({
      moment: "moment"
    })
  ],
  externals: [ "google" ]
};