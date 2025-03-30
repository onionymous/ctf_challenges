// just serve index.html as a very simple web server.
var express = require('express');
var app = express();
app.use(express.static(__dirname + '/public'));
app.listen(3000);