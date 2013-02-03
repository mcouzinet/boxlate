
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , user = require('./routes/user')
  , http = require('http')
  , path = require('path')
  , mongoose = require('mongoose');

var app = express();


var M1 = {'la%20defense', 'chateau%20de%20vincennes'},
    M2 = {'porte%20dauphine', 'nation'},
    M3 = {'pont%20de%20levallois', 'gallieni' },
    M3B = {'porte%20des%20lilas', 'gambetta' },
    M4 = {'porte%20de%20clignancourt', 'porte%20dorleans' ),
    M5 = {'bobigny', 'place%20ditalie' ),
    M6 = {'charles%20de%20gaulle', 'nation' ),
    M7 = {'la%20courneuve', array('mairie%20divry', 'villejuif%20louis%20aragon') ),
    M7B = {'louis%20blanc', 'pre%20saint%20gervais' ),
    // "M8" = {'balard', '' ),
    M9 = {'pont%20de%20sevres', 'mairie%20de%20montreuil' ),
    M10 = {'boulogne', 'gare%20dausterlitz' ),
    M11 = {'chatelet', 'mairie%20des%20lilas' ),
    M12 = {'aubervilliers', 'mairie%20dissy' ),
    M13 = {'saintlazare' , 'chatillon%20montrouge' );

mongoose.connect('mongodb://localhost/boxdate');

var boxAtt = mongoose.Schema({ 
    id: 'string',
    mdp: 'string',
    ligne: []
  }),
  Box = mongoose.model('box', boxAtt);

app.configure(function(){
  app.set('port', process.env.PORT || 3000);
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use(express.favicon());
  app.use(express.logger('dev'));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
  app.use(express.static(path.join(__dirname, 'public')));
});

app.configure('development', function(){
  app.use(express.errorHandler());
});

app.get('/', routes.index);
app.get('/users', user.list);

http.createServer(app).listen(app.get('port'), function(){
  console.log("Express server listening on port " + app.get('port'));
});


var options = {
  host: 'localhost',
  port: 8080,
  path: '/?from=bourse&to=nation&sens=1'
};


http.get(options, function(res) {
  res.on("data", function(chunk) {
    console.log(JSON.parse(chunk)[0].steps[0].time);
    //console.log(chunk);

  });
}).on('error', function(e) {
  console.log("Got error: " + e.message);
});
