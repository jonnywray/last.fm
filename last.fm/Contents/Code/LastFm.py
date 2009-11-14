import string, datetime, Helper
from PMS import *

# Dictonary keys
AUTH_KEY = "authentication"
SUBSCRIBE = "subscribe"

# API
SECRET = "95305a7a167653058d921994b58eaf3b"
KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

# User authentication
AUTHENTICATE_URL = API_BASE +"auth.getMobileSession&username=%s&authToken=%s"+ API_KEY + "&api_sig=%s"

# Album
ALBUM_INFO = API_BASE + "album.getinfo&artist=%s&album=%s" + API_KEY

# Artists
USER_RECOMMENDED_ARTISTS = API_BASE + "user.getRecommendedArtists" + API_KEY + "&api_sig=%s&sk=%s"
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY

# Tag
TAG_TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TAG_TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
TAG_TOP_ALBUMS = API_BASE + "tag.gettopalbums&tag=%s" + API_KEY
TAG_TOP_TRACKS = API_BASE + "tag.gettoptracks&tag=%s" + API_KEY
TAG_SIMILAR_TAG = API_BASE + "tag.getsimilar&tag=%s" + API_KEY
TAG_WEEKLY_ARTIST_CHART = API_BASE + "tag.getweeklyartistchart&tag=%s" + API_KEY

# Track
TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY

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
        
        tag = Tag(tagName, tagCount)
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
    
    
####################################################################################################
# Class definitions
####################################################################################################
class Album:
    def __init__(self, name, artist):
        self.name = name
        self.artist = artist
        self.directImage = None
        self.tagCount = None
        self.playCount = None
          
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
            
            
#####################################################
class Artist:
    def __init__(self, name):
        self.name = name
        self.directImage = None
        self.tagCount = None
        self.playCount = None
        
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
class Tag:
    def __init__(self, name, tagCount):
        self.name = name
        self.tagCount = tagCount
        
    def getArtistChart(self):
        url = TAG_WEEKLY_ARTIST_CHART % self.name
        artists = []
        for artistElement in XML.ElementFromURL(url).xpath('/lfm/weeklyartistchart/artist'):
            name = artistElement.xpath("name")[0].text
            artist = Artist(name, includeExtendedMetadata)
            artists.append(artist)
        return artists
    
    def getTopArtists(self):
        url = TAG_TOP_ARTISTS % String.Quote(self.name)
        return Artist.GetTopArtists(url)
    
    def getTopTracks(self):
        url = TAG_TOP_TRACKS % String.Quote(self.name)
        return Track.GetTopTracks(url)
    
    def getTopAlbums(self):
        url = TAG_TOP_ALBUMS % String.Quote(self.name)
        return Album.TopAlbums(url)
    
    artistChart = property(getArtistChart)
    topArtists = property(getTopArtists)
    topTracks = property(getTopTracks)
    topAlbums = property(getTopAlbums)
    
    
#####################################################
class Track:
    def __init__(self, name, artist, url):
        self.name = name
        self.artist = artist
        self.url = url
        self.tagCount = None
        self.playCount = None
        self.__canStream = None
        self.__directImage = None
        self.overrideUser = False
    
    
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
            
            track = Track(name, artist, url)
            track.streamable = int(trackElement.xpath("streamable")[0].text) == 1
            track.tagCount = TagCount(trackElement)
            track.playCount = PlayCount(trackElement)
            tracks.append(track)
        
        totalPages = int(XML.ElementFromURL(url).xpath('/lfm/tracks')[0].get('totalPages'))
        morePages = page < totalPages
        return (tracks, morePages)
    
    def getTopTags(self):
       url = USER_TOP_TAGS % String.Quote(self.name)
       return Tag.TopTags(url)

    def getTopArtists(self):
       url = USER_TOP_ARTISTS % String.Quote(self.name)
       return Artist.TopArtists(url)
        
    def getTopAlbums(self):
       url = USER_TOP_ALBUMS % String.Quote(self.name)
       return Album.TopAlbums(url)
    
    def getTopTracks(self):
       url = USER_TOP_TRACKS % String.Quote(self.name)
       return Track.TopTracks(url)
    
    title = property(getTitle)
    friends = property(getFriends)
    neighbours = property(getNeighbours)
    topTags = property(getTopTags)
    topArtists = property(getTopArtists)
    topAlbums = property(getTopAlbums)
    topTracks = property(getTopTracks)
    libraryArtists = property(getLibraryArtists)
    libraryAlbums = property(getLibraryAlbums)
    
    