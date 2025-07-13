"use strict"

const largeModule = require('./largeModule');

module.exports = async (event, context) => {
    return context
        .status(200)
        .succeed("Hello from Node.js with large module!");
}
