const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: './src/index.js',
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
         'contentBase': './dist',
         'writeToDisk': true,
         'watchContentBase': true
  },
  module: {
  rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/,/pyodide/],
        use: {
          loader: "babel-loader"
        }
      },
      {test: /\.py$/,
       use: 'raw-loader'
      }
  ]},
  plugins: [
    new CleanWebpackPlugin(),
    new HtmlWebpackPlugin({
      title: 'Development'
    }),
    new CopyPlugin([
      {from: 'src/pyodide/*.data',
       to: '',
       flatten: true
      },
      {from: 'src/pyodide/*.json',
       to: '',
       flatten: true
      },
      {from: 'src/pyodide/*.js',
       to: '',
       flatten: true
      },
      {from: 'src/pyodide/*.wasm',
       to: '',
       flatten: true
      },
    ])
  ],
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  }
};
