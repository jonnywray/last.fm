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
TAG_TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
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

DISPLAY_METADATA = "displayMetaData"

#######################################################################
def SearchTags(query, page=1):
  tags = []
  url = SEARCH_TAGS % (String.Quote(query, True), page)
  Log(url)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/tagmatches/tag'):
    tagName = item.xpath('name')[0].text
    tag = Tag(tagName)
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
    artist = Artist(name)
    artist.image = Image(item)
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
    artist = item.xpath('artist')[0].text
    
    album = Album(name, artist)
    album.image = Image(item)
    albums.append(album)
  
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  more = startIndex + itemsPerPage < total
  return (albums, more)


##########################################################################
def TopAlbums(url):
    albums = []
    for albumElement in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
        name = albumElement.xpath("name")[0].text.strip()
        artist = albumElement.xpath("artist/name")[0].text.strip()
         
        album = Album(name, artist)
        album.image = Image(albumElement)
        album.tagCount = TagCount(albumElement)
        album.playCount = PlayCount(albumElement)
        albums.append(album)
    return albums

### Factory for recommended artists
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
        artist = Artist(name)
        artist.image = image
        artists.append(artist)
    return artists

########################################
def TopArtists(url):
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artistElement.xpath("name")[0].text.strip()
           
        artist = Artist(name)
        artist.image = Image(artistElement)
        artist.tagCount = TagCount(artistElement)
        artist.playCount = PlayCount(artistElement)
        artists.append(artist)
        
    return artists

#######################################################################
def TagTopTags():
    return TopTags(TAG_TOP_TAGS)    


##########################################################################
def TopTracks(url):
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        streamable = int(trackElement.xpath("streamable")[0].text.strip())
        name = trackElement.xpath("name")[0].text.strip()
        artist = trackElement.xpath("artist/name")[0].text.strip()
        trackUrl = TrackUrl(trackElement)
        
        track = Track(name, artist, trackUrl)
        track.image = Image(trackElement)
        track.streamable = streamable
        track.tagCount = TagCount(trackElement)
        track.playCount = PlayCount(trackElement)
        tracks.append(track)
        
    return tracks

#######################################################################
def TopTags(url):
    tags = [] 
    for tagItem in XML.ElementFromURL(url).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        
        tag = Tag(tagName)
        tag.tagCount = tagCount
        tags.append(tag)
    return tags

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
def CurrentUser():
    if Prefs.Get(LOGIN_PREF_KEY) == None:
        return None
    else:
        user = User(Prefs.Get(LOGIN_PREF_KEY), None, None)
        return user

##########################################
# How do I force a reauthentication when user parameters are changed?
def IsAuthenticated():
    if Dict.Get(AUTH_KEY) == None:
        Authenticate()
    return Dict.Get(AUTH_KEY) != None

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
    
    
####################################################################################################
# Class definitions
#    TODO: the getInfo method is more or less common to a lot of classes. Better solution needed
####################################################################################################
class Album:
    def __init__(self, name, artist):
        self.name = name
        self.artist = artist
        self.directImage = None
        self.tagCount = None
        self.playCount = None
          
    def addToLibrary(self):
        params = dict()
        params['method'] = 'library.addAlbum'
        params['album'] = self.name.encode('utf-8')
        params['artist'] = self.artist.encode('utf-8')
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = LIBRARY_ADD_ALBUM % (String.Quote(self.artist), String.Quote(self.name), apiSig, sessionKey)
        # values forces a POST
        result = HTTP.Request(url, values={})
        
    def getSummary(self):
        albumInfo = self.__albumInfo()
        summary = None
        if albumInfo != None:
            items = albumInfo.xpath('/lfm/album/wiki/summary')
            if len(items) > 0 and items[0].text != None:
                summary = String.StripTags(items[0].text)
        return summary

    def setImage(self, image):
        self.directImage = image
        
    def getImage(self):
        if self.directImage != None:
            return self.directImage
        else:
            albumInfo = self.__albumInfo()
            image = None
            if albumInfo != None:
                items = albumInfo.xpath('/lfm/album')
                if len(items) > 0:
                    image = Image(items[0])
            return image
        
    def getTrackList(self):
        tracks = []
        albumInfo = self.__albumInfo()
        if albumInfo != None:
            albumId = albumInfo.xpath('/lfm/album/id')[0].text
            playlistName = "lastfm://playlist/album/" + albumId
            playListUrl = PLAYLIST_FETCH % playlistName
            for trackElement in XML.ElementFromURL(playListUrl).xpath('//ns:playlist/ns:trackList/ns:track', namespaces=PLAYLIST_NS):
                name = trackElement.xpath("ns:title", namespaces=PLAYLIST_NS)[0].text
                artist = trackElement.xpath("ns:creator", namespaces=PLAYLIST_NS)[0].text.strip()
                trackUrl = trackElement.xpath("ns:identifier", namespaces=PLAYLIST_NS)[0].text + "?autostart"
            
                track = Track(name, artist, trackUrl)
                tracks.append(track)
        return tracks
    
    def getListeners(self):
        info = self.__albumInfo()
        if info == None:
            return None
        else:
            infoElements = info.xpath('/lfm/album/listeners')
            if len(infoElements) == 0:
                return None
            else:
                return int(infoElements[0].text)
            
    def getPlays(self):
        if self.playCount != None:
            return self.playCount
        else:
            info = self.__albumInfo()
            if info == None:
                return None
            else:
                infoElements = info.xpath('/lfm/album/playcount')
                if len(infoElements) == 0:
                    return None
                else:
                    return int(infoElements[0].text)
    
    
    listeners = property(getListeners)
    plays = property(getPlays)
    trackList = property(getTrackList)
    summary = property(getSummary)
    image = property(getImage, setImage)
    
    def __albumInfo(self):
        includeExtendedMetadata = Prefs.Get(DISPLAY_METADATA)
        if not includeExtendedMetadata:
            return None
        else:
            try:
                infoUrl =  ALBUM_INFO % (String.Quote(self.artist, True), String.Quote(self.name, True))
                return XML.ElementFromURL(infoUrl)
            except:
                return None
            
class Video:
    def __init__(self, title, thumb, videoUrl):
        self.title = title
        self.thumb = thumb
        self.videoUrl = videoUrl
        
    def isYouTube(self):
        return (self.thumb.find('youtube.com') > -1) or (self.thumb.find('ytimg.com') > -1)
    
    def getVideoId(self):
        if self.isYouTube():
            return self.videoUrl.split('/')[-1].replace('+1-','')
        else:
            return self.videoUrl.split('/')[-1]

    videoId = property(getVideoId)
    
    
#####################################################
class Artist:
    def __init__(self, name):
        self.name = name
        self.directImage = None
        self.tagCount = None
        self.playCount = None
        self.__canStream = None

    def addToLibrary(self):
        params = dict()
        params['method'] = 'library.addArtist'
        params['artist'] = self.name.encode('utf-8')
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = LIBRARY_ADD_ARTIST % (String.Quote(self.name), apiSig, sessionKey)
        # values forces a POST
        result = HTTP.Request(url, values={})
        Log(result)
        
    # Scraping. Videos aren't covered by the API
    def getVideos(self, page):
        videos = []
        url = ARTIST_VIDEOS % (String.Quote(self.name), page)
        for video in XML.ElementFromURL(url, True, errors="ignore").xpath('//ul[@class="clearit videos  mediumVideoList"]/li'):
            title = video.xpath("a/strong")[0].text
            thumb = video.xpath("a//img")[0].get('src')
            path = video.xpath("a")[0].get('href')
            videoUrl = BASE_URL % path
            videos.append(Video(title, thumb, videoUrl))
        more = len(XML.ElementFromURL(url, True, errors="ignore").xpath('//a[@class="nextlink"]')) > 0
        return (videos, more)
    
    def getSummary(self):
        artistInfo = self.__artistInfo()
        summary = None
        if artistInfo != None:
            items = artistInfo.xpath('/lfm/artist/bio/summary')
            if len(items) > 0 and items[0].text != None:
                summary = String.StripTags(items[0].text)
        return summary

    def setImage(self, image):
        self.directImage = image
        
    def getImage(self):
        if self.directImage != None:
            return self.directImage
        else:
            artistInfo = self.__artistInfo()
            image = None
            if artistInfo != None:
                items = artistInfo.xpath('/lfm/artist')
                if len(items) > 0:
                    image = Image(items[0])
            return image
            
    def setStreamable(self, flag):
        self.__canStream = flag
        
    def getStreamable(self):
        if self.__canStream != None:
            return self.__canStream
        else:
            info = self.__artistInfo()
            if info == None:
                return False
            else:
                infoElements = info.xpath('/lfm/artist/streamable')
                if len(infoElements) == 0:
                    return False
                else:
                    return infoElements[0].text == "1"
            
    def getSimilarArtistsRadio(self):
        stationName = "artist/%s/similarartists" % String.Quote(self.name, True)
        return Radio(stationName)
    
    def getAlbums(self):
        albums = []
        url = ARTIST_ALBUMS % String.Quote(self.name, True)
        for albumElement in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
            name = albumElement.xpath("name")[0].text
            
            album = Album(name, self.name)
            album.image = Image(albumElement)
            album.tagCount = TagCount(albumElement)
            album.playCount = PlayCount(albumElement)
            albums.append(album)
        return albums
    
    def getTracks(self):
        tracks = []
        url = ARTIST_TRACKS % String.Quote(self.name, True)
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
            name = trackElement.xpath("name")[0].text
            trackUrl = TrackUrl(trackElement)
            
            track = Track(name, self.name, trackUrl)
            track.image = Image(trackElement)
            track.streamable = int(trackElement.xpath("streamable")[0].text) == 1
            track.playCount = PlayCount(trackElement)
            tracks.append(track)
        return tracks
    
    def getSimilarArtists(self):
        artists = []
        url = ARTIST_SIMILAR % String.Quote(self.name, True)
        for artistElement in XML.ElementFromURL(url).xpath('/lfm/similarartists/artist'):
            
            artist = Artist(artistElement.xpath("name")[0].text)
            artist.image = Image(artistElement)
            artist.tagCount = TagCount(artistElement)
            artist.playCount = PlayCount(artistElement)
            artists.append(artist)
        return artists
    
    
    def getListeners(self):
        info = self.__artistInfo()
        if info == None:
            return None
        else:
            infoElements = info.xpath('/lfm/artist/stats/listeners')
            if len(infoElements) == 0:
                return None
            else:
                return int(infoElements[0].text)
            
    def getPlays(self):
        if self.playCount != None:
            return self.playCount
        else:
            info = self.__artistInfo()
            if info == None:
                return None
            else:
                infoElements = info.xpath('/lfm/artist/stats/playcount')
                if len(infoElements) == 0:
                    return None
                else:
                    return int(infoElements[0].text)
    
    listeners = property(getListeners)
    plays = property(getPlays)
    similarArtists = property(getSimilarArtists)
    tracks = property(getTracks)
    albums = property(getAlbums)
    similarArtistsRadio = property(getSimilarArtistsRadio)
    streamable = property(getStreamable, setStreamable)
    summary = property(getSummary)
    image = property(getImage, setImage)
    
    def __artistInfo(self):
        includeExtendedMetadata = Prefs.Get(DISPLAY_METADATA)
        if not includeExtendedMetadata:
            return None
        else:
            try:
                infoUrl =  ARTIST_INFO % (String.Quote(self.name, True))
                return XML.ElementFromURL(infoUrl)
            except:
                return None
        

#####################################################
class Radio:
    def __init__(self, stationName):
        self.flashUrl = FLASH_RADIO_BASE % stationName
        self.stationUrl = LASTFM_STATION_FORMAT % stationName
        self.stationName = stationName
        self.tuned = False
        self.playList = []
        
    def len(self):
        return len(self.playList)
    
    def nextTrack(self):
        if len(self.playList) <= 1:
            self.__fetchTracks()
        track = self.playList.pop()
        return track
    
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
        #Log(result)
        
        for trackItem in XML.ElementFromString(result).xpath("/lfm/xspf:playlist/xspf:trackList/xspf:track", namespaces=XSPF_NAMESPACE):
            title = trackItem.xpath('xspf:title', namespaces=XSPF_NAMESPACE)[0].text
            artist = trackItem.xpath('xspf:creator', namespaces=XSPF_NAMESPACE)[0].text
            image = trackItem.xpath('xspf:image', namespaces=XSPF_NAMESPACE)[0].text
            location = trackItem.xpath('xspf:location', namespaces=XSPF_NAMESPACE)[0].text
            track = Track(title, artist, location=location)
            track.image = image
            self.playList.insert(0, track)
        
#####################################################
class Tag:
    def __init__(self, name):
        self.name = name
        self.__radio = Radio("globaltags/%s" % String.Quote(self.name, True))
    
    def getRadio(self):
        Log("*********** Tag get radio "+self.name)
        return self.__radio
    
    # TODO: make sure the time frame is correct here
    def getArtistChart(self):
        url = TAG_WEEKLY_ARTIST_CHART % self.name
        artists = []
        for artistElement in XML.ElementFromURL(url).xpath('/lfm/weeklyartistchart/artist'):
            name = artistElement.xpath("name")[0].text
            artist = Artist(name)
            artists.append(artist)
        return artists
    
    def getTopArtists(self):
        url = TAG_TOP_ARTISTS % String.Quote(self.name)
        return TopArtists(url)
    
    def getTopTracks(self):
        url = TAG_TOP_TRACKS % String.Quote(self.name)
        return TopTracks(url)
    
    def getTopAlbums(self):
        url = TAG_TOP_ALBUMS % String.Quote(self.name)
        return TopAlbums(url)
    
    def getSimilarTags(self):
        tags = []
        url = TAG_SIMILAR_TAG % (String.Quote(self.name, True))
        for tagElement in XML.ElementFromURL(url).xpath('/lfm/similartags/tag'):
            tagName = tagElement.xpath("name")[0].text
            tagCount = TagCount(tagElement)
        
            tag = Tag(tagName)
            tag.tagCount = tagCount
            tags.append(tag)
        return tags  
    
    radio = property(getRadio)
    similarTags = property(getSimilarTags)
    artistChart = property(getArtistChart)
    topArtists = property(getTopArtists)
    topTracks = property(getTopTracks)
    topAlbums = property(getTopAlbums)
    
    
#####################################################
class Track:
    def __init__(self, name, artist, url=None, location=None):
        self.name = name
        self.artist = artist
        self.url = url
        self.location = location
        self.tagCount = None
        self.playCount = None
        self.__canStream = None
        self.__directImage = None
        self.overrideUser = False
    
    def addToLibrary(self):
        params = dict()
        params['method'] = 'library.addTrack'
        params['track'] = self.namec
        params['artist'] = self.artist.encode('utf-8')
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = LIBRARY_ADD_TRACK % (String.Quote(self.artist), String.Quote(self.name), apiSig, sessionKey)
        Log(url)
        # values forces a POST
        result = HTTP.Request(url, values={})
        Log(result)
        
    def ban(self):
        params = dict()
        params['method'] = 'track.ban'
        params['track'] = self.name.encode('utf-8')
        params['artist'] = self.artist.encode('utf-8')
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = TRACK_BAN % (String.Quote(self.name), String.Quote(self.artist), apiSig, sessionKey)
        # values forces a POST
        result = HTTP.Request(url, values={})
        Log(result)
        
    def love(self):
        params = dict()
        params['method'] = 'track.love'
        params['track'] = self.name.encode('utf-8')
        params['artist'] = self.artist.encode('utf-8')
        sessionKey = Dict.Get(AUTH_KEY)
        params['sk'] = sessionKey
        apiSig = CreateApiSig(params)
        url = TRACK_LOVE % (String.Quote(self.name), String.Quote(self.artist), apiSig, sessionKey)
        # values forces a POST
        result = HTTP.Request(url, values={})
    
    def getSummary(self):
        trackInfo = self.__trackInfo()
        summary = None
        if trackInfo != None:
            items = trackInfo.xpath('/lfm/track/wiki/summary')
            if len(items) > 0 and items[0].text != None:
                summary = String.StripTags(items[0].text)
        return summary

    def setImage(self, image):
        self.__directImage = image
        
    def getImage(self):
        if self.__directImage != None:
            return self.__directImage
        else:
            trackInfo = self.__trackInfo()
            image = None
            if trackInfo != None:
                items = trackInfo.xpath('/lfm/track/album')
                if len(items) > 0:
                    image = Image(items[0])
            return image
            
    def setStreamable(self, flag):
        self.__canStream = flag
        
    def getStreamable(self):
        if self.__canStream != None:
            return self.__canStream
        else:
            trackInfo = self.__trackInfo()
            if trackInfo == None:
                return False
            else:
                infoElements = trackInfo.xpath('/lfm/track/streamable')
                if len(infoElements) == 0:
                    return False
                else:
                    return infoElements[0].text == "1"
            
    def getListeners(self):
        info = self.__trackInfo()
        if info == None:
            return None
        else:
            infoElements = info.xpath('/lfm/track/listeners')
            if len(infoElements) == 0:
                return None
            else:
                return int(infoElements[0].text)
            
    def getPlays(self):
        if self.playCount != None:
            return self.playCount
        else:
            info = self.__trackInfo()
            if info == None:
                return None
            else:
                infoElements = info.xpath('/lfm/track/playcount')
                if len(infoElements) == 0:
                    return None
                else:
                    return int(infoElements[0].text)
    
    listeners = property(getListeners)
    plays = property(getPlays)
    streamable = property(getStreamable, setStreamable)
    summary = property(getSummary)
    image = property(getImage, setImage)
        
    def __trackInfo(self):
        if self.overrideUser:
            includeExtendedMetadata = True
        else:
            includeExtendedMetadata = Prefs.Get(DISPLAY_METADATA)
        if not includeExtendedMetadata:
            return None
        else:
            try:
                infoUrl =  TRACK_INFO % (String.Quote(self.artist, True), String.Quote(self.name, True))
                return XML.ElementFromURL(infoUrl)
            except:
                return None
            
    
#####################################################        
class User:
   
    def __init__(self, name, realName, image):
        self.name = name
        self.realName = realName
        self.image = image

    def getLovedRadio(self):
        stationName = "user/%s/loved" % self.name
        return Radio(stationName)
    
    def getLibraryRadio(self):
        stationName = "user/%s/library" % self.name
        return Radio(stationName)
    
    def getNeighoursRadio(self):
        stationName = "user/%s/neighbours" % self.name
        return Radio(stationName)
    
    def getRecommendedRadio(self):
        stationName = "user/%s/recommended" % self.name
        return Radio(stationName)
    
    def getTitle(self):
        if self.realName == None:
            return self.name
        else:
            return self.realName + " ("+self.name+")"
         
    def getLovedTracks(self, page):
        url = USER_LOVED_TRACKS % (self.name, page)
        tracks = []
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/lovedtracks/track'):
            name = trackElement.xpath("name")[0].text.strip()
            artist = trackElement.xpath("artist/name")[0].text.strip()
            trackUrl = "http://" + TrackUrl(trackElement)
            
    # LovedTracks does not return streamable there must use detailed meta-data
            track = Track(name, artist, trackUrl)
            track.overrideUser = True
            track.image = Image(trackElement)
            tracks.append(track)
                
        totalPages = int(XML.ElementFromURL(url).xpath('/lfm/lovedtracks')[0].get('totalPages'))
        morePages = page < totalPages
        return (tracks, morePages)
    
    def getRecentTracks(self):
        url = USER_RECENT_TRACKS % self.name
        tracks = []
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/recenttracks/track'):
            streamable = int(trackElement.xpath("streamable")[0].text.strip())
            name = trackElement.xpath("name")[0].text.strip()
            artist = trackElement.xpath("artist")[0].text.strip()
            trackUrl = TrackUrl(trackElement)
            
            track = Track(name, artist, trackUrl)
            track.image = Image(trackElement)
            tracks.append(track)
        return tracks

    def getFriends(self):
        url = USER_FRIENDS % self.name
        users = []
        for friend in XML.ElementFromURL(url).xpath('/lfm/friends/user'):
            name = friend.xpath("name")[0].text.strip()
            realName = None
            if len(friend.xpath("realname")) > 0:
                realName = friend.xpath("realname")[0].text
            image = Image(friend)
            user = User(name, realName, image)
            users.append(user)
        return users
                
    def getNeighbours(self):
        url = USER_NEIGHBOURS % self.name
        users = []
        for neighbour in XML.ElementFromURL(url).xpath('/lfm/neighbours/user'):
            name = neighbour.xpath("name")[0].text.strip()
            realName = None
            image = Image(neighbour)
            user = User(name, realName, image)
            users.append(user)
        return users

    def getLibraryAlbums(self):
        url = LIBRARY_ALBUMS % self.name
        albums = []
        for albumElement in XML.ElementFromURL(url).xpath('/lfm/albums/album'):
            name = albumElement.xpath("name")[0].text.strip()
            artist = albumElement.xpath("artist/name")[0].text.strip()
            
            album = Album(name, artist)
            album.image = Image(albumElement)
            album.tagCount = TagCount(albumElement)
            album.playCount = PlayCount(albumElement)
            albums.append(album)
        return albums

    def getLibraryArtists(self):
        url = LIBRARY_ARTISTS % self.name
        artists = []
        for artistElement in XML.ElementFromURL(url).xpath('/lfm/artists/artist'):
            name = artistElement.xpath("name")[0].text.strip()
            
            artist = Artist(name)
            artist.image = Image(artistElement)
            artist.tagCount = TagCount(artistElement)
            artist.playCount = PlayCount(artistElement)
            artists.append(artist)
        return artists
    
    def getLibraryTracks(self, page):
        url = LIBRARY_TRACKS % (self.name, page)
        tracks = []
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/tracks/track'): 
            name = trackElement.xpath("name")[0].text.strip()
            artist = trackElement.xpath("artist/name")[0].text.strip()
            trackUrl = TrackUrl(trackElement)
            
            track = Track(name, artist, trackUrl)
            track.streamable = int(trackElement.xpath("streamable")[0].text) == 1
            track.tagCount = TagCount(trackElement)
            track.playCount = PlayCount(trackElement)
            tracks.append(track)
        
        totalPages = int(XML.ElementFromURL(url).xpath('/lfm/tracks')[0].get('totalPages'))
        morePages = page < totalPages
        return (tracks, morePages)
    
    def getTopTags(self):
       url = USER_TOP_TAGS % String.Quote(self.name)
       return TopTags(url)

    def getTopArtists(self):
       url = USER_TOP_ARTISTS % String.Quote(self.name)
       return TopArtists(url)
        
    def getTopAlbums(self):
       url = USER_TOP_ALBUMS % String.Quote(self.name)
       return TopAlbums(url)
    
    def getTopTracks(self):
       url = USER_TOP_TRACKS % String.Quote(self.name)
       return TopTracks(url)
    
    def getIsCurrentUser(self):
        return self.name == CurrentUser().name
    
    ########################################################
    # TODO: actually return something useful, but what?
    def RecentStations(self):
        pageLimit = 50
        params = dict()
        params['method'] = 'user.getRecentStations'
        params['user'] = userName
        params['limit'] = str(pageLimit)
        params['sk'] = Dict.Get(AUTH_KEY)
        apiSig = CreateApiSig(params)
        
        url = USER_RECENT_STATIONS % (userName, pageLimit, apiSig, sessionKey)
        for station in XML.ElementFromURL(url).xpath('/lfm/recentstations/station'):
            name = station.xpath("name")[0].text
            url = station.xpath("url")[0].text
            image = Image(station.xpath('resources/resource')[0])
        return None
    
    isCurrentUser = property(getIsCurrentUser)
    title = property(getTitle)
    recentTracks = property(getRecentTracks)
    friends = property(getFriends)
    neighbours = property(getNeighbours)
    topTags = property(getTopTags)
    topArtists = property(getTopArtists)
    topAlbums = property(getTopAlbums)
    topTracks = property(getTopTracks)
    libraryArtists = property(getLibraryArtists)
    libraryAlbums = property(getLibraryAlbums)
    lovedRadio = property(getLovedRadio)
    libraryRadio = property(getLibraryRadio)
    neighoursRadio = property(getNeighoursRadio)
    recommendedRadio = property(getRecommendedRadio)
    
    
    