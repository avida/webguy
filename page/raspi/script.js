
var twitch_page = 0
var games_page = 0
var current_game = ""
var browseGames = true

function twitchStreamHandle(data)
{
   var list = JSON.parse(data)
   $('#twitch-lst-dir').empty()
   for (stream in list ){
      var title = list[stream][0]
      var url = list[stream][1]
      var img = list[stream][2]
      var viewers = list[stream][3]
      $('#twitch-lst-dir').append(format('<li class="fileItem" twitch_url="%s"><img class="game-thumb" src="%s">%s<span class="ui-li-count">%s</span></li>', [url, img, title, viewers]))
      }
   $('#twitch-lst-dir').listview('refresh')
   $.mobile.loading("hide")
   browseGames = false;
}

function twitchGamesHandle(data)
{
    var list =  JSON.parse(data)
    $('#twitch-lst-dir').empty()
    for (game in list) {
        var name = list[game][0]
        var viewers = list[game][1]
        var image = list[game][2]
        $('#twitch-lst-dir').append(format('<li class="fileItem"><img class="game-thumb" src="%s"><div class="game-title">%s</div><span class="ui-li-count">%s</span></li>', [image, name,viewers]))
    }
   $('#twitch-lst-dir').listview('refresh')
   $.mobile.loading("hide")
   browseGames = true;
}

$("#btn-browse-twitch").bind("click", function(event, ui){
   $('#twitch-browser-hdr').text("Twitch")
   window.open('#twitch-browser', '_self')
   $.mobile.loading("show",{ 
      text:'/',
      textVisible:true 
      })
   $.get('srv/twitch/games/' + games_page, twitchGamesHandle)
})

$('#twitch-lst-dir').on('click', 'li', function(){
   var item = $(this).html()
   if (browseGames){
      var game = this.getElementsByClassName('game-title')[0].innerHTML
      current_game = game
      $('#twitch-browser-hdr').text(game)
      $.get(format('srv/twitch/search/%s/%s', [game, twitch_page]), twitchStreamHandle )

   } else {
      var url = this.getAttribute('twitch_url')
      $.get('srv/twitch/play/' + url )
   }

})

$('#twitch-btn-next').bind('click', function(event, ui){
       $.mobile.loading("show",{ 
          text:'Loading',
          textVisible:true 
          })
    if (browseGames){
        games_page++
        $.get('srv/twitch/games/' + games_page, twitchGamesHandle)
        
    } else{
        twitch_page++
        $.get(format('srv/twitch/search/%s/%s', [current_game, twitch_page]), twitchStreamHandle )
    }
})
$('#twitch-btn-prev').bind('click', function(event, ui){
       $.mobile.loading("show",{ 
          text:'Loading',
          textVisible:true 
          })
    if (browseGames){
        games_page--
        if (games_page < 0)  games_page = 0
        $.get('srv/twitch/games/' + games_page, twitchGamesHandle)
        
    } else{
        twitch_page--
        if (twitch_page < 0) twitch_page = 0
        $.get(format('srv/twitch/search/%s/%s', [current_game, twitch_page]), twitchStreamHandle )
    }
})


