import string, datetime, Helper
from PMS import *

# Dictonary keys
AUTH_KEY = "authentication"
SUBSCRIBE = "subscribe"

# Pref keys
LOGIN_PREF_KEY = "login"
PASSWD_PREF_KEY = "passwd"
DISPLAY_METADATA = "displayMetaData"

# API
SECRET = "95305a7a167653058d921994b58eaf3b"
KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

BASE_URL = "http://www.last.fm%s"
# User authentication
AUTHENTICATE_URL = API_BASE +"auth.getMobileSession&username=%s&authToken=%s"+ API_KEY + "&api_sig=%s"

# Album
ALBUM_INFO = API_BASE + "album.getinfo&artist=%s&album=%s" + API_KEY

# Playlist
PLAYLIST_NS  = {'ns':'http://xspf.org/ns/0/'}
PLAYLIST_FETCH = API_BASE + "playlist.fetch&playlistURL=%s" + API_KEY 

# Artists
USER_RECOMMENDED_ARTISTS = API_BASE + "user.getRecommendedArtists" + API_KEY + "&api_sig=%s&sk=%s"
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
ARTIST_SIMILAR = API_BASE + "artist.getsimilar&artist=%s" + API_KEY
ARTIST_TRACKS = API_BASE + "artist.gettoptracks&artist=%s" + API_KEY
ARTIST_ALBUMS = API_BASE + "artist.gettopalbums&artist=%s" + API_KEY
ARTIST_VIDEOS = "http://www.last.fm/music/%s/+videos?page=%d"

# Tag
TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TAG_TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
TAG_TOP_ALBUMS = API_BASE + "tag.gettopalbums&tag=%s" + API_KEY
TAG_TOP_TRACKS = API_BASE + "tag.gettoptracks&tag=%s" + API_KEY
TAG_SIMILAR_TAG = API_BASE + "tag.getsimilar&tag=%s" + API_KEY
TAG_WEEKLY_ARTIST_CHART = API_BASE + "tag.getweeklyartistchart&tag=%s" + API_KEY

# Track
TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY
TRACK_LOVE = API_BASE + "track.love&track=%s&artist=%s" + API_KEY + "&api_sig=%s&sk=%s"
TRACK_BAN = API_BASE + "track.ban&track=%s&artist=%s" + API_KEY + "&api_sig=%s&sk=%s"

# User
USER_INFO = API_BASE + "user.getinfo&user=%s" + API_KEY
USER_FRIENDS = API_BASE + "user.getfriends&user=%s" + API_KEY
USER_NEIGHBOURS = API_BASE + "user.getneighbours&user=%s" + API_KEY
USER_TOP_ARTISTS = API_BASE + "user.gettopartists&user=%s" + API_KEY
USER_TOP_ALBUMS = API_BASE + "user.gettopalbums&user=%s" + API_KEY
USER_TOP_TAGS = API_BASE + "user.gettoptags&user=%s" + API_KEY
USER_TOP_TRACKS = API_BASE + "user.gettoptracks&user=%s" + API_KEY
USER_RECENT_TRACKS = API_BASE + "user.getrecenttracks&user=%s" + API_KEY
USER_RECENT_STATIONS = API_BASE + "user.getRecentStations&user=%s&limit=%d" + API_KEY + "&api_sig=%s&sk=%s"
USER_LOVED_TRACKS = API_BASE + "user.getlovedtracks&user=%s&page=%d" + API_KEY

# Library
LIBRARY_ALBUMS = API_BASE + "library.getalbums&user=%s" + API_KEY
LIBRARY_ARTISTS = API_BASE + "library.getartists&user=%s" + API_KEY
LIBRARY_TRACKS = API_BASE + "library.gettracks&user=%s&page=%d"+ API_KEY
LIBRARY_ADD_ALBUM = API_BASE + "library.addAlbum&artist=%s&album=%s" + API_KEY + "&api_sig=%s&sk=%s"
LIBRARY_ADD_ARTIST = API_BASE + "library.addArtist&artist=%s" + API_KEY + "&api_sig=%s&sk=%s"
LIBRARY_ADD_TRACK = API_BASE + "library.addTrack&artist=%s&track=%s" + API_KEY + "&api_sig=%s&sk=%s"

# Search
SEARCH_NAMESPACE   = {'opensearch':'http://a9.com/-/spec/opensearch/1.1/'}
SEARCH_TAGS  = API_BASE + "tag.search&tag=%s&page=%d" + API_KEY
SEARCH_ARTISTS = API_BASE + "artist.search&artist=%s&page=%d" + API_KEY
SEARCH_ALBUMS = API_BASE + "album.search&album=%s&page=%d" +API_KEY

# Radio
BITRATE = 128
XSPF_NAMESPACE = {'xspf':'http://xspf.org/ns/0/'}
RADIO_TUNE = API_BASE + "radio.tune&station=%s" + API_KEY + "&api_sig=%s&sk=%s"
RADIO_GET_PLAYLIST = API_BASE + "radio.getPlaylist&bitrate="+str(BITRATE) + API_KEY + "&api_sig=%s&sk=%s"

FLASH_RADIO_BASE = "http://www.last.fm/listen/%s"
LASTFM_STATION_FORMAT = "lastfm://%s"

#######################################################################
def SearchTags(query, page=1):
  tags = []
  url = SEARCH_TAGS % (String.Quote(query, True), page)
  Log(url)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/tagmatches/tag'):
    tagName = item.xpath('name')[0].text
    tag = (tagName, )
    tags.append(tag)
  
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  more = startIndex + itemsPerPage < total
  return (tags, more)
  
#######################################################################
def SearchArtists(query, page):
  artists = []
  url = SEARCH_ARTISTS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/artistmatches/artist'):
    name = item.xpath('name')[0].text
    image = Image(item)
    artist = (name, image)
    artists.append(artist)
    
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  more = startIndex + itemsPerPage < total
  return (artists, more)
  
##########################################################################
def SearchAlbums(query, page):
  albums = []
  url = SEARCH_ALBUMS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/albummatches/album'):
    name = item.xpath('name')[0].text
    artistName = item.xpath('artist')[0].text
    image = Image(item)
    album = (name, artistName, image)
    albums.append(album)
  
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  more = startIndex + itemsPerPage < total
  return (albums, more)


#######################################################################
def GlobalTopTags():
    return TopTags(TOP_TAGS)    

#######################################################################
def TagTopArtists(tagName):
    url = TAG_TOP_ARTISTS % String.Quote(tagName)
    return TopArtists(url)

#######################################################################
def TagTopAlbums(tagName):
    url = TAG_TOP_ALBUMS % String.Quote(tagName)
    return TopAlbums(url)

#######################################################################
def TagTopTracks(tagName):
    url = TAG_TOP_TRACKS % String.Quote(tagName)
    return TopTracks(url)

##########################################################################
def TopTracks(url):
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        streamable = int(trackElement.xpath("streamable")[0].text.strip())
        trackName = trackElement.xpath("name")[0].text.strip()
        artist = trackElement.xpath("artist/name")[0].text.strip()
        trackUrl = TrackUrl(trackElement)
        image = Image(trackElement)
        track = (trackName, artist, image, trackUrl, streamable)
        tracks.append(track)
    return tracks

##########################################################################
def TopAlbums(url):
    albums = []
    for albumElement in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
        name = albumElement.xpath("name")[0].text.strip()
        artistName = albumElement.xpath("artist/name")[0].text.strip()
        image = Image(albumElement)
        album = (name, artistName, image)
        albums.append(album)
    return albums

#######################################################################
def TopTags(url):
    tags = [] 
    for tagItem in XML.ElementFromURL(url).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tag = (tagName, )
        tags.append(tag)
    return tags

#######################################################################
def SimilarTags(tag):
    tags = []
    url = TAG_SIMILAR_TAG % (String.Quote(tag[0], True))
    for tagElement in XML.ElementFromURL(url).xpath('/lfm/similartags/tag'):
        tagName = tagElement.xpath("name")[0].text
        similar = (tagName, )
        tags.append(similar)
    return tags  

########################################
def AlbumTrackList(artistName, albumName):
    tracks = []
    albumInfo = XML.ElementFromURL( ALBUM_INFO % (String.Quote(artistName, True), String.Quote(albumName, True)))
    albumId = albumInfo.xpath('/lfm/album/id')[0].text
    playlistName = "lastfm://playlist/album/" + albumId
    playListUrl = PLAYLIST_FETCH % playlistName
    for trackElement in XML.ElementFromURL(playListUrl).xpath('//ns:playlist/ns:trackList/ns:track', namespaces=PLAYLIST_NS):
        trackName = trackElement.xpath("ns:title", namespaces=PLAYLIST_NS)[0].text
        artist = trackElement.xpath("ns:creator", namespaces=PLAYLIST_NS)[0].text.strip()
        trackUrl = trackElement.xpath("ns:identifier", namespaces=PLAYLIST_NS)[0].text + "?autostart"
        trackInfo = XML.ElementFromURL(TRACK_INFO % (String.Quote(artistName, True), String.Quote(trackName, True)))
        image = None
        items = trackInfo.xpath('/lfm/track/album')
        if len(items) > 0:
            image = Image(items[0])
        
        streamable = False
        infoElements = trackInfo.xpath('/lfm/track/streamable')
        if len(infoElements) > 0:
            streamable  = infoElements[0].text == "1"
        track = (trackName, artist, image, trackUrl, streamable)
        tracks.append(track)
    return tracks

########################################
def TopArtists(url):
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artistElement.xpath("name")[0].text.strip()
        image = Image(artistElement)
        artist = (name, image)
        artists.append(artist)
    return artists

########################################
def RecommendedArtists():    
    sessionKey = Dict.Get(AUTH_KEY)
    
    params = dict()
    params['method'] = 'user.getRecommendedArtists'
    params['sk'] = sessionKey
    apiSig = CreateApiSig(params)
    
    artists = []
    url = USER_RECOMMENDED_ARTISTS % (apiSig, sessionKey)
    for artist in XML.ElementFromURL(url).xpath('/lfm/recommendations/artist'):
        name = artist.xpath("name")[0].text.strip()
        image = Image(artist)
        artist = (name, image)
        artists.append(artist)
    return artists

########################################
def Friends(userName):
    url = USER_FRIENDS % userName
    users = []
    for friend in XML.ElementFromURL(url).xpath('/lfm/friends/user'):
        name = friend.xpath("name")[0].text.strip()
        realName = None
        if len(friend.xpath("realname")) > 0:
            realName = friend.xpath("realname")[0].text
        image = Image(friend)
        user = (name, realName, image)
        users.append(user)
    return users
                
########################################
def Neighbours(userName):
    url = USER_NEIGHBOURS % userName
    users = []
    for neighbour in XML.ElementFromURL(url).xpath('/lfm/neighbours/user'):
        name = neighbour.xpath("name")[0].text.strip()
        realName = None
        if len(neighbour.xpath("realname")) > 0:
            realName = neighbour.xpath("realname")[0].text
        image = Image(neighbour)
        user = (name, realName, image)
        users.append(user)
    return users

########################################
def LovedTracks(user, page):
    url = USER_LOVED_TRACKS % (user, page)
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/lovedtracks/track'):
        name = trackElement.xpath("name")[0].text.strip()
        artistName = trackElement.xpath("artist/name")[0].text.strip()
        trackUrl = "http://" + TrackUrl(trackElement)
        image = Image(trackElement)
            
    # LovedTracks does not return streamable there must use detailed meta-data
        trackInfo =  XML.ElementFromURL(TRACK_INFO % (String.Quote(artistName, True), String.Quote(name, True)))
        streamable = False
        infoElements = trackInfo.xpath('/lfm/track/streamable')
        if len(infoElements) > 0:
            streamable = infoElements[0].text == "1"
        
        track = (name, artistName, image, trackUrl, streamable)
        tracks.append(track)
                
    totalPages = int(XML.ElementFromURL(url).xpath('/lfm/lovedtracks')[0].get('totalPages'))
    morePages = page < totalPages
    return (tracks, morePages)
    
    
########################################
def RecentTracks(user):
    url = USER_RECENT_TRACKS % user
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/recenttracks/track'):
        streamable = int(trackElement.xpath("streamable")[0].text.strip())
        name = trackElement.xpath("name")[0].text.strip()
        artistName = trackElement.xpath("artist")[0].text.strip()
        trackUrl = TrackUrl(trackElement)
        image = Image(trackElement)
        track = (name, artistName, image, trackUrl, streamable)
        tracks.append(track)
    return tracks

########################################
def LibraryArtists(user):
    url = LIBRARY_ARTISTS % user
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/artists/artist'):
        name = artistElement.xpath("name")[0].text.strip()
        image = Image(artistElement)
        artist = (name, image)
        artists.append(artist)
    return artists
    
########################################
def LibraryAlbums(user):
    url = LIBRARY_ALBUMS % user
    albums = []
    for albumElement in XML.ElementFromURL(url).xpath('/lfm/albums/album'):
        name = albumElement.xpath("name")[0].text.strip()
        artistName = albumElement.xpath("artist/name")[0].text.strip()
        image = Image(albumElement)
        album = (name, artistName, image)
        albums.append(album)
    return albums
    
########################################
def LibraryTracks(user, page):
    url = LIBRARY_TRACKS % (user, page)
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/tracks/track'): 
        name = trackElement.xpath("name")[0].text.strip()
        artistName = trackElement.xpath("artist/name")[0].text.strip()
        trackUrl = TrackUrl(trackElement)
        image = Image(trackElement)
        streamable = int(trackElement.xpath("streamable")[0].text) == 1
        track = (name, artistName, image, trackUrl, streamable)
        tracks.append(track)
        
    totalPages = int(XML.ElementFromURL(url).xpath('/lfm/tracks')[0].get('totalPages'))
    morePages = page < totalPages
    return (tracks, morePages)
    
########################################
def SimilarArtists(artistName):
        artists = []
        url = ARTIST_SIMILAR % String.Quote(artistName, True)
        for artistElement in XML.ElementFromURL(url).xpath('/lfm/similarartists/artist'):
            
            name = artistElement.xpath("name")[0].text
            image = Image(artistElement)
            artist = (name, image)
            artists.append(artist)
        return artists
    
########################################
def ArtistAlbums(artistName):
        albums = []
        url = ARTIST_ALBUMS % String.Quote(artistName, True)
        for albumElement in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
            name = albumElement.xpath("name")[0].text
            image = Image(albumElement)
            album = (name, artistName, image)
            albums.append(album)
        return albums
    
########################################
def ArtistTracks(artistName):
        tracks = []
        url = ARTIST_TRACKS % String.Quote(artistName, True)
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
            name = trackElement.xpath("name")[0].text
            trackUrl = TrackUrl(trackElement)
            image = Image(trackElement)
            streamable = int(trackElement.xpath("streamable")[0].text) == 1
            track = (name, artistName, image, trackUrl, streamable)
            tracks.append(track)
        return tracks
    
########################################
def ArtistVideos(artistName, page):
    videos = []
    url = ARTIST_VIDEOS % (String.Quote(artistName), page)
    for video in XML.ElementFromURL(url, True, errors="ignore").xpath('//ul[@class="clearit videos  mediumVideoList"]/li'):
        title = video.xpath("a/strong")[0].text
        thumb = video.xpath("a//img")[0].get('src')
        path = video.xpath("a")[0].get('href')
        videoUrl = BASE_URL % path
        video = (title, thumb, videoUrl)
        videos.append(video)
    more = len(XML.ElementFromURL(url, True, errors="ignore").xpath('//a[@class="nextlink"]')) > 0
    return (videos, more)


##########################################
def TrackUrl(element):
    return element.xpath("url")[0].text.strip() + "?autostart"

##########################################
def TagCount(element):
    if len(element.xpath("tagcount")) > 0:
        return int(element.xpath("tagcount")[0].text)
    else:
        return None
    
##########################################
def PlayCount(element):
    if len(element.xpath("playcount")) > 0:
        return int(element.xpath("playcount")[0].text)
    else:
        return None
    
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

##########################################
def UserDetails(user):
    url = USER_INFO % String.Quote(user)
    realName = ""
    realNameItems = XML.ElementFromURL(url).xpath('/lfm/user/realname')
    if len(realNameItems) > 0:
        realName = realNameItems[0].text
    image = None
    imageItems = XML.ElementFromURL(url).xpath('/lfm/user/image')
    if len(imageItems) > 0:
        image = imageItems[0].text
    return (realName, image)
    
##########################################
def IsCurrentUser(user):
    if Prefs.Get(LOGIN_PREF_KEY) == None:
        return False
    return user == Prefs.Get(LOGIN_PREF_KEY)

##########################################
def CurrentUser():
    if Prefs.Get(LOGIN_PREF_KEY) == None:
        return None
    else:
        return Prefs.Get(LOGIN_PREF_KEY)

##########################################
def IsAuthenticated():
    if Dict.Get(AUTH_KEY) == None:
        Authenticate()
    return Dict.Get(AUTH_KEY) != None

def IsSubscriber():
    if Dict.Get(SUBSCRIBE) == None:
        Authenticate()
    return Dict.Get(SUBSCRIBE) == '1'

####################################################################################################
def Authenticate():
    Dict.Set(AUTH_KEY, None)
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
    
#####################################################
class Radio:
    def __init__(self, stationName):
        self.stationUrl = LASTFM_STATION_FORMAT % stationName
        self.stationName = stationName
        self.tuned = False
        self.playList = []
    
    def nextTrack(self):
        if len(self.playList) == 0:
            self.__fetchTracks()
        track = self.playList.pop()
        return track
    
    def length(self):
        if len(self.playList) == 0:
            self.__fetchTracks()
        return len(self.playList)
    
    def __tune(self):
        Log("Tuning radio "+self.stationUrl)
        params = dict()
        params['method'] = 'radio.tune'
        params['station'] = self.stationName
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = RADIO_TUNE % (self.stationName, apiSig, sessionKey)
        result = HTTP.Request(url, values={}, cacheTime=0)
        self.tuned = True
        
    def __fetchTracks(self):
        Log("Fetching tracks for "+self.stationUrl)
        if not self.tuned:
            self.__tune()
        params = dict()
        params['method'] = 'radio.getPlaylist'
        params['bitrate'] = str(BITRATE)
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = RADIO_GET_PLAYLIST % (apiSig, sessionKey)
        result = HTTP.Request(url, values={}, cacheTime=0)
        Log(result)
        
        for trackItem in XML.ElementFromString(result).xpath("/lfm/xspf:playlist/xspf:trackList/xspf:track", namespaces=XSPF_NAMESPACE):
            title = trackItem.xpath('xspf:title', namespaces=XSPF_NAMESPACE)[0].text
            artist = trackItem.xpath('xspf:creator', namespaces=XSPF_NAMESPACE)[0].text
            image = trackItem.xpath('xspf:image', namespaces=XSPF_NAMESPACE)[0].text
            location = trackItem.xpath('xspf:location', namespaces=XSPF_NAMESPACE)[0].text
            duration = int(trackItem.xpath('xspf:duration', namespaces=XSPF_NAMESPACE)[0].text)
            track = (title, artist, image, location, duration)
            self.playList.insert(0, track)
    
    