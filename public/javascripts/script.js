$(function() {
  $(".chzn-select").chosen({no_results_text: "No results matched"});

  $('#select-stops').submit(function(){
    $("#my-stops").html('<p style="font-size:16px; text-align:center;">Loading</p>');
    $.ajax({
      url: "getJSON",
      data: $(this).serialize(),
    }).done(function(res){
      if(res.error){
        $("#my-stops").html('<p style="font-size:16px; text-align:center;">'+res.error+'</p>');
      } else {
        $("#my-stops").html('<h3>Vers : '+res.destination1+'</h3><p>'+res.time1+'</p><br /><h3>Vers : '+res.destination2+'</h3><p>'+res.time2+'</p>' );
      }
    });
    return false;
  })

});