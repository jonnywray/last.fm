import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from LastFm import *
from LastFmEntities import *

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
TAG_TOP_TRACKS = API_BASE + "tag.gettoptracks&tag=%s" + API_KEY
TAG_SIMILAR_TAG = API_BASE + "tag.getsimilar&tag=%s" + API_KEY
TAG_WEEKLY_ARTIST_CHART = API_BASE + "tag.getweeklyartistchart&tag=%s" + API_KEY

# Library
LIBRARY_ALBUMS = API_BASE + "library.getalbums&user=%s" + API_KEY
LIBRARY_ARTISTS = API_BASE + "library.getartists&user=%s" + API_KEY
LIBRARY_TRACKS = API_BASE + "library.gettracks&user=%s&page=%d"+ API_KEY

# Artists
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
ARTIST_SIMILAR = API_BASE + "artist.getsimilar&artist=%s" + API_KEY
ARTIST_TRACKS = API_BASE + "artist.gettoptracks&artist=%s" + API_KEY
ARTIST_ALBUMS = API_BASE + "artist.gettopalbums&artist=%s" + API_KEY

# Playlist
PLAYLIST_NS  = {'ns':'http://xspf.org/ns/0/'}
PLAYLIST_FETCH = API_BASE + "playlist.fetch&playlistURL=%s" + API_KEY 

# Tracks
TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY
TRACK_LOVE = API_BASE + "track.love&track=%s&artist=%s" + API_KEY + "&api_sig=%s&sk=%s"

# User
USER_RECOMMENDED_ARTISTS = API_BASE + "user.getRecommendedArtists" + API_KEY + "&api_sig=%s&sk=%s"
USER_TOP_ARTISTS = API_BASE + "user.gettopartists&user=%s" + API_KEY
USER_TOP_ALBUMS = API_BASE + "user.gettopalbums&user=%s" + API_KEY
USER_TOP_TAGS = API_BASE + "user.gettoptags&user=%s" + API_KEY
USER_TOP_TRACKS = API_BASE + "user.gettoptracks&user=%s" + API_KEY
USER_RECENT_TRACKS = API_BASE + "user.getrecenttracks&user=%s" + API_KEY
USER_RECENT_STATIONS = API_BASE + "user.getRecentStations&user=%s&limit=%d" + API_KEY + "&api_sig=%s&sk=%s"
USER_LOVED_TRACKS = API_BASE + "user.getlovedtracks&user=%s&page=%d" + API_KEY

# Search
SEARCH_NAMESPACE   = {'opensearch':'http://a9.com/-/spec/opensearch/1.1/'}
SEARCH_TAGS  = API_BASE + "tag.search&tag=%s&page=%d" + API_KEY
SEARCH_ARTISTS = API_BASE + "artist.search&artist=%s&page=%d" + API_KEY
SEARCH_ALBUMS = API_BASE + "album.search&album=%s&page=%d" +API_KEY

AUTHENTICATE_URL = API_BASE +"auth.getMobileSession&username=%s&authToken=%s"+ API_KEY + "&api_sig=%s"

# Context keys
NAME = "name"
ARTIST = "artist"

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

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, "Last.fm", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.fm'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
####################################################################################################
def CreatePrefs():
  Prefs.Add(id=DISPLAY_METADATA, type='bool', default=False, label='Display artist biography and track information (slower navigation)')
  Prefs.Add(id=LOGIN_PREF_KEY,    type='text', default=None, label='Login')
  Prefs.Add(id=PASSWD_PREF_KEY, type='text', default=None, label='Password', option='hidden')
  
##################################
def MainMenu():
    Authenticate()
    dir = MediaContainer(mediaType='video') 
    if Dict.Get(AUTH_KEY) != None:
        dir.Append(Function(DirectoryItem(Library, "Library", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
        dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
        dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
      #  if Dict.Get(SUBSCRIBE) == '1':
      #      dir.Append(Function(DirectoryItem(RecentStations, "Recent Stations", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
        dir.Append(Function(DirectoryItem(RecommendedArtists, "Recommended Artists", thumb=R(ICON))))
        dir.Append(Function(DirectoryItem(Friends, "Friends", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
        dir.Append(Function(DirectoryItem(Neighbours, "Neighbours", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
        
    dir.Append(Function(DirectoryItem(TopTags, "Top Tags", thumb=R(ICON)), url = TAG_TOP_TAGS))
    dir.Append(Function(InputDirectoryItem(SearchAlbums, title=L("Search Albums ..."), prompt=L("Search Albums"), thumb=R('search.png'))))
    dir.Append(Function(InputDirectoryItem(SearchArtists, title=L("Search Artists ..."), prompt=L("Search Artists"), thumb=R('search.png'))))
    dir.Append(Function(InputDirectoryItem(SearchTags, title=L("Search Tags ..."), prompt=L("Search Tags"), thumb=R('search.png'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    

########################################################
def Friends(sender, userName):
    dir = MediaContainer(title2=sender.itemTitle)
    for friend in LastFm.Friends(userName):
        dir.Append(Function(DirectoryItem(User, title=friend.title, thumb=friend.image), name = friend.name))
    return dir

########################################################
def Neighbours(sender, userName):
    dir = MediaContainer(title2=sender.itemTitle)
    for neighbour in LastFm.Neighbours(userName):
        dir.Append(Function(DirectoryItem(User, title=neighbour.title, thumb=neighbour.image), name = neighbour.name))
    return dir

########################################################
def User(sender, name):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(Library, "Library", thumb=R(ICON)), userName = name))
    dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks", thumb=R(ICON)), userName = name))
    dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks", thumb=R(ICON)), userName = name))
    #if Dict.Get(SUBSCRIBE) == '1':
    #    dir.Append(Function(DirectoryItem(RecentStations, "Recent Stations", thumb=R(ICON)), userName = name))
    dir.Append(Function(DirectoryItem(TopArtists, "Top Artists", thumb=R(ICON)), url=USER_TOP_ARTISTS % String.Quote(name)))
    dir.Append(Function(DirectoryItem(TopAlbums, "Top Albums", thumb=R(ICON)), url=USER_TOP_ALBUMS % String.Quote(name)))
    dir.Append(Function(DirectoryItem(TopTracks, "Top Tracks", thumb=R(ICON)), url=USER_TOP_TRACKS % String.Quote(name)))
    dir.Append(Function(DirectoryItem(TopTags, "Top Tags", thumb=R(ICON)), url=USER_TOP_TAGS % String.Quote(name)))
    dir.Append(Function(DirectoryItem(Friends, "Friends", thumb=R(ICON)), userName = name))
    dir.Append(Function(DirectoryItem(Neighbours, "Neighbours", thumb=R(ICON)), userName = name))
    return dir


########################################################
def Library(sender, userName):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(LibraryAlbums, "Albums", thumb=R(ICON)), userName = userName))
    dir.Append(Function(DirectoryItem(LibraryArtists, "Artists", thumb=R(ICON)), userName = userName))
    dir.Append(Function(DirectoryItem(LibraryTracks, "Tracks", thumb=R(ICON)), userName = userName))
    return dir

########################################################
def LibraryAlbums(sender, userName): 
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for album in LastFm.LibraryAlbums(userName, Prefs.Get(DISPLAY_METADATA)):
        subtitle = None
        if album.tagCount != None:
            subtitle = "Tag Count: " + album.tagCount
        elif album.playCount:
            subtitle = "Play Count: " + album.playCount
        title = album.name + " - " + album.artist
        dir.Append(Function(DirectoryItem(Album, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary), artist = album.artist, album = album.name))
    return dir


########################################################
def LibraryArtists(sender, userName):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for artist in LastFm.LibraryArtists(userName, Prefs.Get(DISPLAY_METADATA)):
        subtitle = None
        if artist.tagCount != None:
            subtitle = "Tag Count: " + artist.tagCount
        elif artist.playCount:
            subtitle = "Play Count: " + artist.playCount
        dir.Append(Function(DirectoryItem(Artist, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary), artist = artist.name, image=artist.image, summary=artist.summary))
    return dir

########################################################
def LibraryTracks(sender, userName, page=1):
    menu = ContextMenu(includeStandardItems=False)
    menu.Append(Function(DirectoryItem(LoveTrack, title="Love Track")))
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu)
    tracksTuple = LastFm.LibraryTracks(userName, page, Prefs.Get(DISPLAY_METADATA))
    for track in tracksTuple[0]:
        if track.streamable:
            subtitle = None
            if track.tagCount != None:
                subtitle = "Tag Count: " + track.tagCount
            elif track.playCount:
                subtitle = "Play Count: " + track.playCount
            
            title = track.name + " - " + track.artist
            dir.Append(WebVideoItem(track.url, title=title, thumb=track.image, subtitle=subtitle, summary=track.summary, 
                                    contextKey=title, contextArgs={NAME:track.name, ARTIST:track.artist}))
      
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LibraryTracks, "More ...", thumb=R(ICON)), userName = userName, page = page+1))
    return dir
      
########################################################
def RecommendedArtists(sender):    
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    sessionKey = Dict.Get(AUTH_KEY)
    
    params = dict()
    params['method'] = 'user.getRecommendedArtists'
    params['sk'] = sessionKey
    apiSig = CreateApiSig(params)
    
    url = USER_RECOMMENDED_ARTISTS % (apiSig, sessionKey)
    for artist in XML.ElementFromURL(url).xpath('/lfm/recommendations/artist'):
        name = artist.xpath("name")[0].text
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, subtitle=None, summary=summary), artist = name, image=image, summary=summary))
    return dir
    
########################################################
# Only valid for API statations as this is the url returned
def RecentStations(sender, userName):
    dir = MediaContainer(title2=sender.itemTitle)
    sessionKey = Dict.Get(AUTH_KEY)
    pageLimit = 50
    params = dict()
    params['method'] = 'user.getRecentStations'
    params['user'] = userName
    params['limit'] = str(pageLimit)
    params['sk'] = sessionKey
    apiSig = CreateApiSig(params)
    
    url = USER_RECENT_STATIONS % (userName, pageLimit, apiSig, sessionKey)
    for station in XML.ElementFromURL(url).xpath('/lfm/recentstations/station'):
        name = station.xpath("name")[0].text
        url = station.xpath("url")[0].text
        image = Image(station.xpath('resources/resource')[0])
        # TODO: radio API not web video item
        dir.Append(WebVideoItem(url, title=name, thumb=image))
    return dir
  
##########################################################################
def LovedTracks(sender, userName, page=1):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = USER_LOVED_TRACKS % (userName, page)
    for track in XML.ElementFromURL(url).xpath('/lfm/lovedtracks/track'):
        name = track.xpath("name")[0].text.strip()
        artist = track.xpath("artist/name")[0].text.strip()
        streamable = XML.ElementFromURL(TRACK_INFO % (String.Quote(artist), String.Quote(name))).xpath('/lfm/track/streamable')[0].text
        if streamable == '1':
            subtitle = None
            trackUrl = "http://" + track.xpath("url")[0].text.strip()
            image = Image(track)
            summary = TrackSummary(artist, name)
            title = name + " - " + artist
            trackUrl = trackUrl + "?autostart"
            dir.Append(WebVideoItem(trackUrl, title=name + " - " + artist, thumb=image, subtitle=subtitle, summary=summary))
    totalPages = int(XML.ElementFromURL(url).xpath('/lfm/lovedtracks')[0].get('totalPages'))
    if page < totalPages:
        dir.Append(Function(DirectoryItem(LovedTracks, "More ...", thumb=R(ICON)), userName = userName, page = page+1))
    return dir

##########################################################################
def RecentTracks(sender, userName):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = USER_RECENT_TRACKS % userName
    for track in XML.ElementFromURL(url).xpath('/lfm/recenttracks/track'):
        streamable = int(track.xpath("streamable")[0].text)
        if streamable == 1:
            name = track.xpath("name")[0].text.strip()
            artist = track.xpath("artist")[0].text.strip()
            subtitle = None
            trackUrl = track.xpath("url")[0].text.strip()
            image = Image(track)
            summary = TrackSummary(artist, name)
            title = name + " - " + artist
            trackUrl = trackUrl + "?autostart"
            dir.Append(WebVideoItem(trackUrl, title=name + " - " + artist, thumb=image, subtitle=subtitle, summary=summary))
    return dir

#######################################################################
def Category(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(TopArtists, "Top Artists", thumb=R(ICON)), url = TAG_TOP_ARTISTS % (String.Quote(tag, True))))
    dir.Append(Function(DirectoryItem(TopAlbums, "Top Albums", thumb=R(ICON)), url = TAG_TOP_ALBUMS % (String.Quote(tag, True))))
    dir.Append(Function(DirectoryItem(TopTracks, "Top Tracks", thumb=R(ICON)), url = TAG_TOP_TRACKS % (String.Quote(tag, True))))
    dir.Append(Function(DirectoryItem(ArtistChart, "Weekly Artist Chart", thumb=R(ICON)), tag=tag))
    dir.Append(Function(DirectoryItem(SimilarTags, "Similar Tags", thumb=R(ICON)), tag=tag))
    return dir

#######################################################################
def ArtistChart(sender, tag):
    dir = MediaContainer(viewGroup='Details',title2=sender.itemTitle) 
    url = TAG_WEEKLY_ARTIST_CHART % tag
    for artist in XML.ElementFromURL(url).xpath('/lfm/weeklyartistchart/artist'):
        name = artist.xpath("name")[0].text
        image = ArtistImage(name)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir

##########################################################################
def TopArtists(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for artist in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artist.xpath("name")[0].text
        subtitle = None
        if len(artist.xpath("tagcount")) > 0:
            tagCount = artist.xpath("tagcount")[0].text
            subtitle = "Tag Count: " + tagCount
        elif len(artist.xpath("playcount")) > 0:
            playCount = artist.xpath("playcount")[0].text
            subtitle = "Play Count: " + playCount
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir

##########################################################################
def TopAlbums(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for album in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
        name = album.xpath("name")[0].text
        artist = album.xpath("artist/name")[0].text
        subtitle = None
        if len(album.xpath("tagcount")) > 0:
            tagCount = album.xpath("tagcount")[0].text
            subtitle = "Tag Count: " + tagCount
        elif len(album.xpath("playcount")) > 0:
            playCount = album.xpath("playcount")[0].text
            subtitle = "Play Count: " + playCount
        image = Image(album)
        summary = AlbumSummary(artist, name)
        title = name + " - " + artist
        dir.Append(Function(DirectoryItem(Album, title=title, subtitle=subtitle, thumb=image, summary=summary), artist = artist, album=name))
    return dir

##########################################################################
def TopTracks(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for track in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        streamable = int(track.xpath("streamable")[0].text)
        if streamable == 1:
            name = track.xpath("name")[0].text
            artist = track.xpath("artist/name")[0].text
            subtitle = None
            if len(track.xpath("tagcount")) > 0:
                tagCount = track.xpath("tagcount")[0].text
                subtitle = "Tag Count: " + tagCount
            elif len(track.xpath("playcount")) > 0:
                playCount = track.xpath("playcount")[0].text
                subtitle = "Play Count: " + playCount
            
            trackUrl = track.xpath("url")[0].text.strip()
            image = Image(track)
            summary = TrackSummary(artist, name)
            title = name + " - " + artist
            trackUrl = trackUrl + "?autostart"
            dir.Append(WebVideoItem(trackUrl, title=name, thumb=image, subtitle=subtitle, summary=summary))
    return dir

#######################################################################
def TopTags(sender, url):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for tagItem in XML.ElementFromURL(url).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        subtitle = "Tag Count: " + tagCount
        dir.Append(Function(DirectoryItem(Category, title=tagName.capitalize(), subtitle=subtitle, thumb=R(ICON)), tag = tagName))
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
        image = TrackImage(artist, title)
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
          trackUrl = track.xpath("url")[0].text + "?autostart"
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

#######################################################
def SimilarArtists(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = ARTIST_SIMILAR % String.Quote(artist, True)
    for artist in XML.ElementFromURL(url).xpath('/lfm/similarartists/artist'):
        name = artist.xpath("name")[0].text
        match = artist.xpath("match")[0].text
        subtitle = "Match: " + match + "%"
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
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
def SearchAlbums(sender, query, page=1):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  url = SEARCH_ALBUMS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/albummatches/album'):
    name = item.xpath('name')[0].text
    artist = item.xpath('artist')[0].text
    image = Image(item)
    summary = AlbumSummary(artist, name)
    dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, summary=summary), artist = name, image=image, summary=summary))
  
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  if startIndex + itemsPerPage < total:
      dir.Append(Function(DirectoryItem(SearchArtists, "More ...", thumb=R(ICON)), query = query, page = page+1))
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


########################################################
def LoveTrack(sender, key, **kwargs):
    track = kwargs[NAME].encode('utf-8')
    artist = kwargs[ARTIST].encode('utf-8')
    sessionKey = Dict.Get(AUTH_KEY)
    params = dict()
    params['method'] = 'track.love'
    params['track'] = track
    params['artist'] = artist
    params['sk'] = sessionKey
    apiSig = CreateApiSig(params)
    url = TRACK_LOVE % (String.Quote(track), String.Quote(artist), apiSig, sessionKey)
    # values forces a POST
    result = HTTP.Request(url, values={})
    Log(result)
    
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
def AlbumImage(artist, album):
    infoUrl = None
    try:
        infoUrl = ALBUM_INFO % (String.Quote(artist, True), String.Quote(album, True))
    except:
        pass
    image = R(ICON)
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        album = XML.ElementFromURL(infoUrl).xpath('/lfm/album')
        image = Image(album[0])
    return image

##########################################
def TrackImage(artist, name):
    infoUrl = None
    try:
        infoUrl = TRACK_INFO % (String.Quote(artist, True), String.Quote(name, True))
    except:
        pass
    image = R(ICON)
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        album = XML.ElementFromURL(infoUrl).xpath('/lfm/track/album')
        if len(album) > 0:
            image = Image(album[0])
    return image

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

##########################################
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
        summaryItems = XML.ElementFromURL(infoUrl, errors="ignore").xpath('/lfm/artist/bio/summary')
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
    
    image = R(ICON)
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
    