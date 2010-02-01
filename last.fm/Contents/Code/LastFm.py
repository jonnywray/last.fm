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
def GlobalTopTags():
    return TopTags(TOP_TAGS)    

#######################################################################
def TagTopArtists(tagName):
    url = TAG_TOP_ARTISTS % String.Quote(tagName)
    return TopArtists(url)

#######################################################################
def TopTags(url):
    tags = [] 
    for tagItem in XML.ElementFromURL(url).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tag = (tagName, )
        tags.append(tag)
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
            duration = int(trackItem.xpath('xspf:duration', namespaces=XSPF_NAMESPACE)[0].text)
            track = (title, artist, image, location, duration)
            self.playList.insert(0, track)
    
    