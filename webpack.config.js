const path = require("path");

console.info("Building in " + process.env.NODE_ENV + " mode.");
module.exports = {
  mode: process.env.NODE_ENV ? "production" : "development",
  entry: {
    index: "./lib/index.ts",
  },
  devtool: process.env.NODE_ENV ? "source-map" : "inline-source-map",
  output: {
    globalObject: 'this',
    library: {
      name: "helpers",
      type: "umd",
    },
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        include: path.resolve(__dirname, "lib"),
        loader: "ts-loader",
      },
    ],
  },
  resolve: {
    extensions: [".ts", ".js"],
    extensionAlias: {
      ".ts": [".js", ".ts"],
    },
  },
};
