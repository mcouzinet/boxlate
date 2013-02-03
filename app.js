
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , user = require('./routes/user')
  , nextTrains = require('./routes/nextTrains')
  , http = require('http')
  , path = require('path')
  , mongoose = require('mongoose');

var app = express();
var myStop = "M3--Bourse";

// mongoose.connect('mongodb://localhost/boxdate');

// var boxAtt = mongoose.Schema({ 
//     id: 'string',
//     mdp: 'string',
//     ligne: []
//   }),
//   Box = mongoose.model('box', boxAtt);

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
app.get('/getJSON', function(req, res, next){
  req.setEncoding('utf8');
  var nexts = [],
      extremes = {
        "M1" : ['la%20defense', 'chateau%20de%20vincennes'],
        "M2" : ['porte%20dauphine', 'nation'],
        "M3" : ['pont%20de%20levallois', 'gallieni'],
        "M3B" : ['porte%20des%20lilas', 'gambetta'],
        "M4" : ['porte%20de%20clignancourt', 'porte%20dorleans'],
        "M5" : ['bobigny', 'place%20ditalie'],
        "M6" : ['charles%20de%20gaulle', 'nation'],
        "M7" : ['la%20courneuve', 'mairie%20divry'],
        "M7B" : ['louis%20blanc', 'pre%20saint%20gervais'],
        // M8" : {'balard', '' ),
        "M9" : ['pont%20de%20sevres', 'mairie%20de%20montreuil'],
        "M10" : ['boulogne', 'gare%20dausterlitz'],
        "M11" : ['chatelet', 'mairie%20des%20lilas'],
        "M12" : ['chatelet', 'mairie%20des%20lilas'],
        "M13" : ['aubervilliers', 'mairie%20dissy'],
        "M14" : ['saintlazare' , 'chatillon%20montrouge']
      }

  if (req.query['metro']){
    myStop = req.query['metro'];
  }

// var stopsLength = typeof stops == "string" ? 1 : stops.length;
var stopsLength = 1;
  for (var i=0; i<stopsLength; i++){
    var line = myStop.split('--')[0],
        stop = myStop.split('--')[1],
        thisExtremes = extremes[line],
        toReturn = {
          'stop': stop
        };

    // console.log('line: ', line, 'stop: ', stop);
    // console.log("thisExtremes: ", thisExtremes, thisExtremes.length);

    // BEGIN extremes loop
    for(j=0; j<2; j++){

      var a = 0,
          options = {
          host: 'localhost',
          port: 8080,
          path: '/?from='+stop+'&to='+thisExtremes[j]+'&sens=1'
        };

      http.get(options, function(result) {
        result.on("data", function(chunk) {
          a++;
          var date = new Date(),
              current_hour = date.getHours(),
              current_minutes = date.getMinutes(),
              trainTime = JSON.parse(chunk)[0].steps[0].time,
              train_hour = trainTime.split(':')[0],
              train_minutes = trainTime.split(':')[1];
          if(current_hour == train_hour ){
            difference = train_minutes - current_minutes;
          } else {
            difference = Math.abs(train_minutes - current_minutes + 60);
          }
          if(difference > 5) { toReturn['color'+a] = 1 }
          else if(difference < 1) { toReturn['color'+a] = 3 }
          else if(difference < 5 && difference > 1) { toReturn['color'+a] = 2 }
          // else {}
          toReturn['destination'+a] = thisExtremes[a-1].replace(/%20/gi, ' ');
          toReturn['time'+a] = trainTime;
          //console.log(chunk);
          if( a == 2 ){
            console.log("OKOKOKOKOKOKKOO");
            res.json(toReturn);
          }
        });
      }).on('error', function(e) {
        console.log("Python--Got error: " + e.message);
      });
    } // END extremes loop

  }
});
app.get('/users', user.list);

http.createServer(app).listen(app.get('port'), function(){
  console.log("Express server listening on port " + app.get('port'));
});
