var fs = require('fs');
var html = fs.readFileSync('site/command/index.html','utf8');
var m = html.match(/<script>([\s\S]*)<\/script>/);
new Function(m[1]);
console.log('JS parses OK, length', m[1].length);
