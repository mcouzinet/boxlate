var http = require('http');


exports.index = function(req, res){
  var stops = req.query['metro'],
      nexts = [],
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

  if (!stops){
    res.json({error: 'no stop selected'});
  }

// var stopsLength = typeof stops == "string" ? 1 : stops.length;
var stopsLength = 1;
  for (var i=0; i<stopsLength; i++){
    var line = typeof stops == "string" ? stops.split('--')[0] : stops[i].split('--')[0],
        stop = typeof stops == "string" ? stops.split('--')[1] : stops[i].split('--')[1],
        stop = stop.replace("/+/gi"," ");
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
          toReturn['destination'+a] = thisExtremes[a-1];
          toReturn['time'+a] = JSON.parse(chunk)[0].steps[0].time;
          //console.log(chunk);
          if( a == 2 ){
            console.log("OKOKOKOKOKOKKOO");
            res.json({
              nexts: toReturn
            });
          }
        });
      }).on('error', function(e) {
        console.log("Python--Got error: " + e.message);
      });
    } // END extremes loop

  }

};