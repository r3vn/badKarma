/*
PhantomJS web screenshot
*/

var system = require('system');
var args = system.args;

var page = require('webpage').create();
page.open(args[1], function() {
  page.viewportSize = { width: 1024, height: 768 };
  var base64 = page.renderBase64('PNG');
  console.log(base64);
  phantom.exit();
});