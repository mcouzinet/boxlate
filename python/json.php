<?php 
function sechour($duree){
	$heures=intval($duree / 3600);
	$minutes=intval(($duree % 3600) / 60);
	$time = "";
	$time.= ($heures>0)? $heures.':' : '';
	$time.= ($minutes>0)? $minutes.'min' : '';
	return ($time);
}

/**** Using Curl to pars and format VIANAVIGO result ****/
$curl = curl_init('http://192.168.2.87:8080/?from=bourse&to=nation&date=1359845678');
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
$return = curl_exec($curl);
$array = json_decode($return, true);

$trajet = count($array); 

for ($i=0; $i <$trajet ; $i++) { 
	$array[$i]['duration'] = sechour($array[$i]['duration']);
	$steps = count($array[$i]['steps']);
	for ($j=0; $j < $steps ; $j++) { 
		$array[$i]['steps'][$j]['time'] = str_replace(':', 'h', $array[$i]['steps'][$j]['time']);
	}
}

$json = json_encode($array);
print_r(utf8_encode($json));
 ?>

