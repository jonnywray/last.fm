import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"

BASE_URL = "http://www.last.fm%s"
# Radio playing works, but it is a blank screen (1x1 flash)
RADIO_PAGE_URL = "http://www.last.fm/listen/artist/%s/similarartists"
# Two video types - Last.FM and YouTube
VIDEOS_PAGE = "http://www.last.fm/music/%s/+videos?page=%d"
VIDEO_PLAY_LIST = "http://ext.last.fm/1.0/video/getplaylist.php?&vid=%s&artist=%s"
YOU_TUBE_PAGE = "http://www.youtube.com/watch?v=%s" 

# API URLs
SECRET = "95305a7a167653058d921994b58eaf3b"
KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

# Album
ALBUM_INFO = API_BASE + "album.getinfo&artist=%s&album=%s" + API_KEY

# Tags
TAG_TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TAG_TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
TAG_TOP_ALBUMS = API_BASE + "tag.gettopalbums&tag=%s" + API_KEY
TAG_TOP_TRACKS = API_BASE + "tag.gettoptracks&tag=d%s" + API_KEY
TAG_SIMILAR_TAG = API_BASE + "tag.getsimilar&tag=%s" + API_KEY
TAG_WEEKLY_ARTIST_CHART = API_BASE + "tag.getweeklyartistchart&tag=%s" + API_KEY

# Libray
LIBRARY_ALBUMS = API_BASE + "library.getalbums&user=%s" + API_KEY
LIBRARY_ARTISTS = API_BASE + "library.getartists&user=%s" + API_KEY
LIBRARY_TRACKS = API_BASE + "library.gettracks&user=%s"+ API_KEY

# Artists
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
SIMILAR_ARTISTS = API_BASE + "artist.getsimilar&artist=%s" + API_KEY
ARTIST_TRACKS = API_BASE + "artist.gettoptracks&artist=%s" + API_KEY
ARTIST_ALBUMS = API_BASE + "artist.gettopalbums&artist=%s" + API_KEY

# Playlist
PLAYLIST_FETCH = API_BASE + "playlist.fetch&playlistURL=%s" + API_KEY 

PLAYLIST_NS  = {'ns':'http://xspf.org/ns/0/'}

# Tracks
TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY

# User
RECOMMENDED_ARTISTS = API_BASE + "user.getRecommendedArtists" + API_KEY + "&api_sig=%s&sk=%s"
USER_FRIENDS = API_BASE + "user.getfriends&user=%s" + API_KEY
USER_NEIGHBOURS = API_BASE + "user.getneighbours&user=%s" + API_KEY

# Search
SEARCH_TAGS  = API_BASE + "tag.search&tag=%s&page=%d" + API_KEY
SEARCH_ARTISTS = API_BASE + "artist.search&artist=%s&page=%d" + API_KEY
SEARCH_NAMESPACE   = {'opensearch':'http://a9.com/-/spec/opensearch/1.1/'}

AUTHENTICATE_URL = API_BASE +"auth.getMobileSession&username=%s&authToken=%s"+ API_KEY + "&api_sig=%s"

# Geo methods seem to be based on country names rather that 2 letter code. 
# Either a Map from code :-> name needed or country from user info
TOP_ARTISTS_CHART = API_BASE + "geo.gettopartists&country=%s" + API_KEY
TOP_TRACKS_CHART = API_BASE + "geo.gettoptracks&country=%s" + API_KEY

# Pref keys
LOGIN_PREF_KEY = "login"
PASSWD_PREF_KEY = "passwd"
DISPLAY_METADATA = "displayMetaData"

# Dictonary keys
AUTH_KEY = "authentication"
SUBSCRIBE = "subscribe"
 
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

# Authenticated ideas:
#   'shouting' an artist (context menu)
#   'share' an artist and track (context menu)
#   'love' and 'ban' a track (context menu)
#   adding tags (context menu)
#   playlist support by displaying and adding tracks
#   all user level charts, friends, etc
#   add scrobbling when playing a track or video 

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, "Last.fm", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.fm'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  Dict.Reset()
  
####################################################################################################
def CreateDict():
    Dict.Set(AUTH_KEY, None)
    Dict.Set(SUBSCRIBE, None)
  
####################################################################################################
def CreatePrefs():
  Prefs.Add(id=DISPLAY_METADATA, type='bool', default=False, label='Display artist biography and track information (slower navigation)')
  Prefs.Add(id=LOGIN_PREF_KEY,    type='text', default=None, label='Login')
  Prefs.Add(id=PASSWD_PREF_KEY, type='text', default=None, label='Password', option='hidden')
  
##################################
def MainMenu():
    Authenticate()
    dir = MediaContainer(mediaType='video') 
    dir.Append(Function(DirectoryItem(TopTags, "Top Tags", thumb=R(ICON))))
    if Dict.Get(AUTH_KEY) != None:
        dir.Append(Function(DirectoryItem(RecommendedArtists, "Recommended Artists", thumb=R(ICON))))
    # TODO: search albums
    dir.Append(Function(InputDirectoryItem(SearchTags, title=L("Search Tags ..."), prompt=L("Search Tags"), thumb=R('search.png'))))
    dir.Append(Function(InputDirectoryItem(SearchArtists, title=L("Search Artists ..."), prompt=L("Search Artists"), thumb=R('search.png'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    
########################################################
def RecommendedArtists(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    sessionKey = Dict.Get(AUTH_KEY)
    
    params = dict()
    params['method'] = 'user.getRecommendedArtists'
    params['sk'] = Dict.Get(AUTH_KEY)
    apiSig = CreateApiSig(params)
    
    url = RECOMMENDED_ARTISTS % (apiSig, sessionKey)
    for artist in XML.ElementFromURL(url).xpath('/lfm/recommendations/artist'):
        name = artist.xpath("name")[0].text
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, subtitle=None, summary=summary), artist = name, image=image, summary=summary))
    return dir
    
#######################################################################
def SearchTags(sender, query, page=1):
  dir = MediaContainer(title2=sender.itemTitle)
  url = SEARCH_TAGS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/tagmatches/tag'):
    tagName = item.xpath('name')[0].text
    dir.Append(Function(DirectoryItem(Category, title=tagName.capitalize()), tag = tagName))
  
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  if startIndex + itemsPerPage < total:
      dir.Append(Function(DirectoryItem(SearchTags, "More ...", thumb=R(ICON)), query = query, page = page+1))
  return dir
  
#######################################################################
def SearchArtists(sender, query, page=1):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  url = SEARCH_ARTISTS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/artistmatches/artist'):
    name = item.xpath('name')[0].text
    image = Image(item)
    summary = ArtistSummary(name)
    dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, summary=summary), artist = name, image=image, summary=summary))
  
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  if startIndex + itemsPerPage < total:
      dir.Append(Function(DirectoryItem(SearchArtists, "More ...", thumb=R(ICON)), query = query, page = page+1))
  return dir
  
#######################################################################
def TopTags(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for tagItem in XML.ElementFromURL(TAG_TOP_TAGS).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        subtitle = "Tag Count: " + tagCount
        dir.Append(Function(DirectoryItem(Category, title=tagName.capitalize(), subtitle=subtitle, thumb=R(ICON)), tag = tagName))
    return dir

#######################################################################
def Category(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(CategoryArtists, "Top Artists", thumb=R(ICON)), tag=tag))
    dir.Append(Function(DirectoryItem(CategoryAlbums, "Top Albums", thumb=R(ICON)), tag=tag))
    dir.Append(Function(DirectoryItem(CategoryTracks, "Top Tracks", thumb=R(ICON)), tag=tag))
    dir.Append(Function(DirectoryItem(ArtistChart, "Weekly Artist Chart", thumb=R(ICON)), tag=tag))
    dir.Append(Function(DirectoryItem(SimilarTags, "Similar Tags", thumb=R(ICON)), tag=tag))
    return dir

#######################################################################
def ArtistChart(sender, tag):
    dir = MediaContainer(viewGroup='Details',title2=sender.itemTitle) 
    url = TAG_WEEKLY_ARTIST_CHART % tag
    for artist in XML.ElementFromURL(url).xpath('/lfm/weeklyartistchart/artist'):
        name = artist.xpath("name")[0].text
        Log(ARTIST_INFO % name)
        image = ArtistImage(name)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir

##########################################################################
def CategoryArtists(sender, tag):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = TAG_TOP_ARTISTS % (String.Quote(tag, True))
    for artist in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artist.xpath("name")[0].text
        tagCount = artist.xpath("tagcount")[0].text
        subtitle = "Tag Count: " + tagCount
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir

##########################################################################
def CategoryAlbums(sender, tag):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = TAG_TOP_ALBUMS % (String.Quote(tag, True))
    for album in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
        name = album.xpath("name")[0].text
        artist = album.xpath("artist/name")[0].text
        tagCount = album.xpath("tagcount")[0].text
        subtitle = "Tag Count: " + tagCount
        image = Image(album)
        summary = AlbumSummary(artist, name)
        title = name + " - " + artist
        dir.Append(Function(DirectoryItem(Album, title=title, subtitle=subtitle, thumb=image, summary=summary), artist = artist, album=name))
    return dir

##########################################################################
def CategoryTracks(sender, tag):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = TAG_TOP_TRACKS % (String.Quote(tag, True))
    for track in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        streamable = int(track.xpath("streamable")[0].text)
        if streamable == 1:
            name = track.xpath("name")[0].text
            artist = track.xpath("artist/name")[0].text
            tagCount = track.xpath("tagcount")[0].text
            url = track.xpath("url")[0].text.strip()
            subtitle = "Tag Count: " + tagCount
            image = Image(track)
            summary = TrackSummary(artist, name)
            title = name + " - " + artist
            trackUrl = url + "?autostart"
            dir.Append(WebVideoItem(trackUrl, title=name, thumb=image, subtitle=subtitle, summary=summary))
    return dir

##########################################################################
def SimilarTags(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    url = TAG_SIMILAR_TAG % (String.Quote(tag, True))
    for tag in XML.ElementFromURL(url).xpath('/lfm/similartags/tag'):
        tagName = tag.xpath("name")[0].text
        dir.Append(Function(DirectoryItem(Category, title=tagName.capitalize(), thumb=R(ICON)), tag = tagName))
    return dir

############################################################################
def Artist(sender, artist, image=None, summary=None):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(ArtistVideos, title="Videos", thumb=image, summary=summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistTracks, title="Tracks", thumb=image, summary=summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistAlbums, title="Albums", thumb=image, summary=summary), artist = artist))
    streamable = XML.ElementFromURL(ARTIST_INFO % String.Quote(artist)).xpath('/lfm/artist/streamable')[0].text
    if streamable == '1':
        radioUrl = RADIO_PAGE_URL % String.Quote(artist, True)
        dir.Append(WebVideoItem(radioUrl, title= "Play "+artist+" Radio", thumb=image, summary=summary))
    dir.Append(Function(DirectoryItem(SimilarArtists, title="Similar Artists", thumb=image, summary=summary), artist = artist))
    return dir

############################################################################
def Album(sender, artist, album):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    infoUrl = ALBUM_INFO % (String.Quote(artist, True), String.Quote(album, True))
    albumId = XML.ElementFromURL(infoUrl).xpath('/lfm/album/id')[0].text
    playlistName = "lastfm://playlist/album/" + albumId
    playListUrl = PLAYLIST_FETCH % playlistName
    for track in XML.ElementFromURL(playListUrl).xpath('//ns:playlist/ns:trackList/ns:track', namespaces=PLAYLIST_NS):
        title = track.xpath("ns:title", namespaces=PLAYLIST_NS)[0].text
        image = None
        if len(track.xpath("ns:image", namespaces=PLAYLIST_NS)) > 0:
            image = track.xpath("ns:image", namespaces=PLAYLIST_NS)[0].text
        trackUrl = track.xpath("ns:identifier", namespaces=PLAYLIST_NS)[0].text
        url = trackUrl + "?autostart"
        summary = TrackSummary(artist, title)
        dir.Append(WebVideoItem(url, title=title + " - " + artist, thumb=image, summary=summary))
    return dir


#######################################################
def ArtistAlbums(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = ARTIST_ALBUMS % String.Quote(artist, True)
    for album in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
        name = album.xpath("name")[0].text
        tagCount = album.xpath("playcount")[0].text
        subtitle = "Play Count: " + tagCount
        image = Image(album)
        summary = AlbumSummary(artist, name)
        title = name + " - " + artist
        dir.Append(Function(DirectoryItem(Album, title=title, subtitle=subtitle, thumb=image, summary=summary), artist = artist, album=name))
    return dir

#######################################################
def ArtistTracks(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = ARTIST_TRACKS % String.Quote(artist, True)
    for track in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        name = track.xpath("name")[0].text
        streamable = track.xpath("streamable")[0].text
        if streamable == "1":
          image = Image(track)
          playcount = track.xpath("playcount")[0].text
          url = track.xpath("url")[0].text
          subtitle = "Play count: " + playcount
          infoUrl = None
          summary = TrackSummary(artist, name)     
          url = track.xpath("url")[0].text + "?autostart"
          dir.Append(WebVideoItem(url, title=name, thumb=image, subtitle=subtitle, summary=summary))
    return dir

#######################################################
def SimilarArtists(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = SIMILAR_ARTISTS % String.Quote(artist, True)
    for artist in XML.ElementFromURL(url).xpath('/lfm/similarartists/artist'):
        name = artist.xpath("name")[0].text
        match = artist.xpath("match")[0].text
        subtitle = "Match: " + match + "%"
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir

##########################################################################
# Scraping. Videos aren't covered by the API. Also, some are from
# Last.FM whereas some are from YouTube. I haven't seen other places
def ArtistVideos(sender, artist, page=1):
    dir = MediaContainer(title2=sender.itemTitle) 
    url = VIDEOS_PAGE % (String.Quote(artist), page)
    for video in XML.ElementFromURL(url, True, errors="ignore").xpath('//ul[@class="clearit videos  mediumVideoList"]/li'):
        title = video.xpath("a/strong")[0].text
        thumb = video.xpath("a//img")[0].get('src')
        path = video.xpath("a")[0].get('href')
        videoUrl = BASE_URL % path
        youTube = (thumb.find('youtube.com') > -1) or (thumb.find('ytimg.com') > -1)
        if(youTube):
           videoId = videoUrl.split('/')[-1].replace('+1-','')
           dir.Append(Function(VideoItem(YouTubeVideo, title=title, thumb=thumb), videoId=videoId))
        else:
           videoId = videoUrl.split('/')[-1]
           dir.Append(Function(VideoItem(LastFmVideo, title=title, thumb=thumb), videoId=videoId, artist=artist))
    if len(XML.ElementFromURL(url, True, errors="ignore").xpath('//a[@class="nextlink"]')) > 0:
        dir.Append(Function(DirectoryItem(ArtistVideos, title="More ..."), artist=artist, page=page+1))
    return dir


##########################################
def AlbumSummary(artist, album):
    infoUrl = None
    try:
        infoUrl = ALBUM_INFO % (String.Quote(artist, True), String.Quote(album, True))
    except:
        pass
    summary = None
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        content = XML.ElementFromURL(infoUrl)
        if content != None:
            items = content.xpath('/lfm/album/wiki/summary')
            if len(items) > 0:
                summary = String.StripTags(items[0].text)
    return summary

##########################################
def TrackSummary(artist, name):
    infoUrl = None
    try:
        infoUrl = TRACK_INFO % (String.Quote(artist, True), String.Quote(name, True))
    except:
        pass
    summary = None
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        content = XML.ElementFromURL(infoUrl).xpath('/lfm/track/wiki/summary')
        if len(content) > 0:
            summary = String.StripTags(content[0].text)
    return summary

def ArtistImage(name):
    infoUrl = None
    try:
        infoUrl = ARTIST_INFO % String.Quote(name)
    except:
        pass
    
    image = None
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        artist = XML.ElementFromURL(infoUrl).xpath('/lfm/artist')
        image = Image(artist[0])
    return image

##########################################
def ArtistSummary(name):
    infoUrl = None
    try:
        infoUrl = ARTIST_INFO % String.Quote(name)
    except:
        pass
    
    summary = None
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        summaryItems = XML.ElementFromURL(infoUrl).xpath('/lfm/artist/bio/summary')
        if len(summaryItems) > 0:
            summaryItem = summaryItems[0].text
            if summaryItem != None:
                summary = String.StripTags(summaryItem.strip())
    return summary

##########################################
def Image(item):
    imageItems = item.xpath('image[@size="extralarge"]')
    if len(imageItems) == 0:
        imageItems = item.xpath('image[@size="large"]')
    if len(imageItems) == 0:
        imageItems = item.xpath('image[@size="medium"]')
    if len(imageItems) == 0:
        imageItems = item.xpath('image[@size="small"]')
            
    image = None
    if len(imageItems) > 0:
        image = imageItems[0].text
    return image

############################################
def LastFmVideo(sender, videoId, artist):
    playList = HTTP.Request(VIDEO_PLAY_LIST % (videoId, String.Quote(artist, True)))
    start = playList.index('<location>') + 10
    stop = playList.index('</location>')
    videoUrl = playList[start:stop]
    return Redirect(videoUrl)
    
############################################
# A little borrowing from the YouTube plugin here. Thanks.
def YouTubeVideo(sender, videoId):
    ytPage = HTTP.Request(YOU_TUBE_PAGE % videoId)
    t = re.findall('"t": "([^"]+)"', ytPage)[0]
    v = re.findall("'VIDEO_ID': '([^']+)'", ytPage)[0] #
    hd = re.findall("'IS_HD_AVAILABLE': ([^,]+),", ytPage)[0] #
    
    fmt = "18"
    if hd == "true":
      fmt = "22"
      
    videoUrl = "http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%s" % (v, t, fmt)
    return Redirect(videoUrl)


####################################################################################################
def Authenticate():
    if Dict.Get(AUTH_KEY) == None:
        userName = Prefs.Get(LOGIN_PREF_KEY)
        password = Prefs.Get(PASSWD_PREF_KEY) 
        if (userName != None) and (password != None):
            GetSession(userName, password)

####################################################################################################
def GetSession(userName, password):
    authToken = Hash.MD5(userName.lower() + Hash.MD5(password))
    params = dict()
    params['authToken'] = authToken
    params['method'] = 'auth.getMobileSession'
    params['username'] = userName
    apiSig = CreateApiSig(params)
    
    url = AUTHENTICATE_URL % (userName, authToken, apiSig)
    response = HTTP.Request(url, cacheTime=0)
    if response != None:
       key = XML.ElementFromString(response).xpath('/lfm/session/key')[0].text
       subscriber = XML.ElementFromString(response).xpath('/lfm/session/subscriber')[0].text
       Dict.Set(AUTH_KEY, key)
       Dict.Set(SUBSCRIBE, subscriber)
    else:
       Dict.Set(AUTH_KEY, None)
       Dict.Set(SUBSCRIBE, None)
       
       
####################################################################################################
def CreateApiSig(params):
        params['api_key'] = KEY
        keys = params.keys()[:]
        keys.sort()
        string = ""
        for name in keys:
            string += name
            string += params[name]
        string += SECRET
        return Hash.MD5(string)
    