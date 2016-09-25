
//-----------------File browser station-------------------------//

function find_longest_substr(s1, s2) {
  // js implementation of algorythm from this article:
  // https://en.wikipedia.org/wiki/Longest_common_substring_problem
  var l = new Array(s1.length)
  for (i = 0; i < s1.length; ++i) {
    l[i] = new Array(s2.length)
  }
  var z = 0;
  var ret = ""
  for (i = 0; i < s1.length; ++i) {
    for (j = 0; j < s2.length; ++j) {
      if (s1[i] == s2[j]) {
        if (i == 0 || j == 0) {
          l[i][j] = 1;
        } else {
          l[i][j] = l[i - 1][j - 1] + 1
        }
        if (l[i][j] > z) {
          z = l[i][j];
          ret = s1.substr(i - z + 1, z)
        } else {
         /*
          if (l[i][j] == z) {
            //ret += s1.substr(i - z + 1, z)
          }*/
        }
      } else {
        l[i][j] = 0;
      }
    }
  }
  return ret;
}

function reduce_lines(str_array) {
  var s1 = str_array[0]
  var s2 = str_array[str_array.length - 1]
  var com_strings = []
  var common_string = find_longest_substr(s1, s2)
  var ind = 0;
  while (common_string.length >= 4) {
    s1 = s1.replace(common_string, "")
    s2 = s2.replace(common_string, "")
    com_strings.push(common_string)
    common_string = find_longest_substr(s1, s2)
    if (++ind > 3) {
      break;
    }
  }
  for (i = 0; i < str_array.length; ++i) {
    for (j = 0; j < com_strings.length; ++j) {
      if (str_array[i].indexOf(com_strings[j]) == -1) {
        com_strings.splice(j, 1)
        break;
      }
    }
  }
  for (i = 0; i < str_array.length; ++i) {
    for (j = 0; j < com_strings.length; ++j) {
      str_array[i] = str_array[i].replace(com_strings[j], "")
    }
  }
  return str_array;
}

var path = []
var last_position = 0

function browseHandle(data){
   var list = JSON.parse(data)
   $('#lst-dir').empty()
   var titles = []

   $('#browser-hdr').text('/'+path.join('/'))
   if(path.length != 0){
      $('#lst-dir').append('<li>..</li>')
   }
   var dirs = list["dirs"]
   var files = list["files"]
   var file_display = files
   if (path.length != 0  && files.length >= 2){
      file_display = reduce_lines(files.slice(0))
   }
   title_to_info = {}
   for (dir in dirs ){
      var title = dirs[dir]
      var el = $('<li>', { class:'dirItem'}).html(title)
      $('#lst-dir').append(el)
      }
   for (file in files ){
      var title = file_display[file]
      var file_name = files[file]
      $('#lst-dir').append(format('<li filename="%s" class="fileItem">%s</li>', [file_name, title]))
      }
   $('#lst-dir').listview('refresh')
   $.mobile.loading("hide")
   $(window).scrollTop(last_position)
}

function itemLoaded(data){
   $.mobile.loading("hide")
}

$('#lst-dir').on('click', 'li', function(){
   var item = $(this).html()
   var isDir = $(this).is(".dirItem")
   $.mobile.loading("show",{ 
      text:item,
      textVisible:true 
      })
   $('input[data-type="search"]').val("");
   if (item == '..'){
      path.pop()
      $('#lst-dir').empty().listview("refresh")
      $.get('srv/browse/'+ path.join('/'), browseHandle)
      return  
   }
   last_position = $(window).scrollTop()
   if (!isDir){
      var filename = this.getAttribute('filename')
      $.get('srv/browse/'+path.join('/')+'/'+filename , itemLoaded)
   } else {
      var id = title_to_info[item]
      path.push(item)
      $('#lst-dir').empty().listview("refresh")
      $.get('srv/browse/'+path.join('/'), browseHandle)
   }
})

$("#btn-browse").bind("click", function(event, ui){
   window.open('#browser', '_self')
   $.mobile.loading("show",{ 
      text:'/',
      textVisible:true 
      })
   $.get('srv/browse/'+path.join('/'), browseHandle)
})
//-----------------Radio station-------------------------//
var current_page = 1
function stationsLoaded(data)
{
   try{
       var stations = JSON.parse(data)
    }
    catch(e){
       window.alert(e.message + "\n Data:\n" + data)
       return
    }
   $('#lst-stations').empty()
   $('#stations-hdr').text('Page ' + current_page)
   for (station in stations)
   {
      var title = stations[station]['name']
      var st_id = stations[station]['id']
      $('#lst-stations').append('<li class="station" st_id="'+st_id+'">'
                                 + title +
                                '</li>')
   }
   $('#lst-stations').listview('refresh')
}
$('#lst-stations').on('click', 'li', function(){
   var item = $(this).html()
    var st_id = this.getAttribute('st_id')
    $.get('srv/radio/play/' + st_id )

})

$('#btn-stations').bind('click', function(event, ui){
   window.open('#stations', '_self')
   $.get('srv/radio/page/'+current_page, stationsLoaded)

})

$('#btn-prev').bind('click', function(event, ui){
    if(current_page > 1){
        $.get('srv/radio/page/' + --current_page, stationsLoaded)
    }
})
$('#btn-next').bind('click', function(event, ui){
    $.get('srv/radio/page/' + ++current_page, stationsLoaded)
})

$('#btn-stop').bind('click', function(event, ui){
    $.get('srv/radio/stop')
})
//-----------------Twitch  -------------------------//
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
      $('#twitch-lst-dir').append(format('<li class="fileItem" twitch_url="%s"><img class="game-thumb" src="%s">%s<span class="ui-li-count">%s</span></li>', [title, img, title, viewers]))
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
//-----------------Youtube staff -------------------------//
$('#btn-youtube').bind('click',function(event, ui){
    window.open('#youtube-page', '_self')  

})

var q;
var nextToken;
var prevToken;
function searchDone(data)
{
    var searchResult = JSON.parse(data)
    nextToken = searchResult.nextToken ? searchResult.nextToken : 0;
    prevToken = searchResult.prevToken ? searchResult.prevToken: 0;
    items = searchResult["items"]
    $('#youtube-search-res').empty()
   for (item in items){
      var video_id = items[item]["id"]
      var title = items[item]["title"]
      var image = items[item]["thumbnail"]
      var date_exp = /(.*)T.*/g
      var date = date_exp.exec(items[item]["published"])[1]
      $('#youtube-search-res').append(format('<li class="video" Id="%s" ><img class="game-thumb" src="%s">%s<span class="ui-li-count">%s</span></li>', [video_id, image, title, date ]))
      }
   $('#youtube-search-res').listview('refresh')
}

function itemOpened(data)
{
  $.mobile.loading("hide")
}

$('#youtube-search-res').on('click', 'li', function(){
   searchType = $("input[name=searchtype]:checked").val()
   var item = $(this).html()
   var id = this.getAttribute('Id')
   $.mobile.loading("show",{ 
      text:'Opening video/playlist',
      textVisible:true 
      })
   if (searchType == "video")
      $.get('srv/youtube/play/'+ id, itemOpened)
   else
      $.get('srv/youtube/playlist/'+ id, itemOpened)
})

$("#search-form").on("submit", function(){
    q =  $("#video-search").val()
   searchType = $("input[name=searchtype]:checked").val()
    $.get('srv/youtube/search/'+q, {"type":searchType}, searchDone)
    return false
})

function changePage(token) {
   searchType = $("input[name=searchtype]:checked").val()
   $.get('srv/youtube/search/'+q, {"token":token, "type": searchType}, searchDone)
}
$("#youtube-btn-prev").on("click", function(){
   changePage(prevToken)
})

$("#youtube-btn-next").on("click", function(){
   changePage(nextToken)
})

// ------------------Music staff------------------//
var music_path = []

function processMusicItems(data){
   var list = JSON.parse(data)
   $.mobile.loading("hide")
   $('#music-items').empty()
   var dirs  = list['dirs']
   var files = list['files']
   for (dir in dirs){
      var el = $('<li>', { class:'dirItem'}).html(dirs[dir])
      $('#music-items').append(el)
   }
   for (file in files){
    var el = $('<li>', { class:'fileItem'}).html(files[file])
      $('#music-items').append(el)

   }
   $('#music-items').listview('refresh')

}

$('#btn-music').bind('click', function(event, ui){
   window.open('#music-page', '_self')
   music_path = []
   $.get('srv/music', processMusicItems)
})

$('#music-items').on('tap', 'li', function(){
   var item = $(this).html()
   var isDir = $(this).is(".dirItem")
   //music_path.push(item)
   $.mobile.loading("show",{ 
      text:item,
      textVisible:true 
      })
   $.get('srv/music/'+ item, itemLoaded)

})
$('#music-items').on('taphold', 'li', function(){
   var item = $(this).html()
   $('#dirPopup').popup()
   $('#popup-msg').html(item)
   $('#dirPopup').popup('open')
})

//--------------------- System staff -------------------/
function updateSystemInfo(data){
//   data = JSON.parse(data)
   $('#uptime').html(data["uptime"])
}

$('#btn-system').on('click', function(event, ui){
   window.open('#system-page', '_self')
   $('#btn-system-audio-hdmi').on('click', function(event,ui){
      $.get('srv/system/hdmi')
   })
   $('#btn-system-audio-analog').on('click', function(event,ui){
      $.get('srv/system/analog')
   })
   $.get('/srv/system/info', updateSystemInfo)

})
//-------------------------/
$('#btn-playlist').on('click', function(event,ui){
$.get('/srv/player/playlist', function(data){
   var list = JSON.parse(data)
   var items = list["items"]
   var plItems = $("#playlist-items")
   plItems.empty()
   for (item in items){
      var el = $('<li>', { pos:item}).html(items[item]['label'])
      plItems.append(el)
   }
   plItems.listview()
   plItems.listview('refresh')
   $('#playlist-items').on('tap', 'li', function(){
      var item = $(this).attr('pos')
     $.get('srv/player/goto/'+ item)

   })
   $("#playlistPopup").popup()
   $("#playlistPopup").popup("open")
})
})
