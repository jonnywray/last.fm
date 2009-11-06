import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

ALBUM_INFO = API_BASE + "album.getinfo&artist=%s&album=%s" + API_KEY
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY

# Library
LIBRARY_ALBUMS = API_BASE + "library.getalbums&user=%s" + API_KEY
LIBRARY_ARTISTS = API_BASE + "library.getartists&user=%s" + API_KEY
LIBRARY_TRACKS = API_BASE + "library.gettracks&user=%s&page=%d"+ API_KEY

# Users
USER_FRIENDS = API_BASE + "user.getfriends&user=%s" + API_KEY
USER_NEIGHBOURS = API_BASE + "user.getneighbours&user=%s" + API_KEY
USER_RECOMMENDED_ARTISTS = API_BASE + "user.getRecommendedArtists" + API_KEY + "&api_sig=%s&sk=%s"
USER_TOP_ARTISTS = API_BASE + "user.gettopartists&user=%s" + API_KEY
USER_TOP_ALBUMS = API_BASE + "user.gettopalbums&user=%s" + API_KEY
USER_TOP_TAGS = API_BASE + "user.gettoptags&user=%s" + API_KEY
USER_TOP_TRACKS = API_BASE + "user.gettoptracks&user=%s" + API_KEY
USER_RECENT_TRACKS = API_BASE + "user.getrecenttracks&user=%s" + API_KEY
USER_RECENT_STATIONS = API_BASE + "user.getRecentStations&user=%s&limit=%d" + API_KEY + "&api_sig=%s&sk=%s"
USER_LOVED_TRACKS = API_BASE + "user.getlovedtracks&user=%s&page=%d" + API_KEY


# TODO: extract the info methods and logic into one place, its the same except xpath
#

#########################################################################
class Tag:
    def __init__(self, name, tagCount):
        self.name = name
        self.tagCount = tagCount
        
#########################################################################
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
        
    def getLovedTracks(self, page, includeExtendedMetadata):
        url = USER_LOVED_TRACKS % (self.name, page)
        tracks = []
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/lovedtracks/track'):
            name = trackElement.xpath("name")[0].text.strip()
            artist = trackElement.xpath("artist/name")[0].text.strip()
            trackUrl = "http://" + TrackUrl(trackElement)
            
            track = Track(name, artist, trackUrl, includeExtendedMetadata)
            track.image = Image(trackElement)
            tracks.append(track)
                
        totalPages = int(XML.ElementFromURL(url).xpath('/lfm/lovedtracks')[0].get('totalPages'))
        morePages = page < totalPages
        return (tracks, morePages)
    
    def getRecentTracks(self, includeExtendedMetadata):
        url = USER_RECENT_TRACKS % self.name
        tracks = []
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/recenttracks/track'):
            streamable = int(trackElement.xpath("streamable")[0].text.strip())
            name = trackElement.xpath("name")[0].text.strip()
            artist = trackElement.xpath("artist")[0].text.strip()
            trackUrl = TrackUrl(trackElement)
            
            track = Track(name, artist, trackUrl, includeExtendedMetadata)
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

    def getLibraryAlbums(self, includeExtendedMetadata):
        url = LIBRARY_ALBUMS % self.name
        albums = []
        for albumElement in XML.ElementFromURL(url).xpath('/lfm/albums/album'):
            name = albumElement.xpath("name")[0].text.strip()
            artist = albumElement.xpath("artist/name")[0].text.strip()
            
            album = Album(name, artist, includeExtendedMetadata)
            album.image = Image(albumElement)
            album.tagCount = TagCount(albumElement)
            album.playCount = PlayCount(albumElement)
            albums.append(album)
        return albums

    def getLibraryArtists(self, includeExtendedMetadata):
        url = LIBRARY_ARTISTS % self.name
        artists = []
        for artistElement in XML.ElementFromURL(url).xpath('/lfm/artists/artist'):
            name = artistElement.xpath("name")[0].text.strip()
            
            artist = Artist(name, includeExtendedMetadata)
            artist.image = Image(artistElement)
            artist.tagCount = TagCount(artistElement)
            artist.playCount = PlayCount(artistElement)
            artists.append(artist)
        return artists
    
    def getLibraryTracks(self, page, includeExtendedMetadata):
        url = LIBRARY_TRACKS % (self.name, page)
        tracks = []
        for trackElement in XML.ElementFromURL(url).xpath('/lfm/tracks/track'): 
            name = trackElement.xpath("name")[0].text.strip()
            artist = trackElement.xpath("artist/name")[0].text.strip()
            trackUrl = TrackUrl(trackElement)
            
            track = Track(name, artist, url, includeExtendedMetadata)
            track.streamable = int(trackElement.xpath("streamable")[0].text) == 1
            track.tagCount = TagCount(trackElement)
            track.playCount = PlayCount(trackElement)
            tracks.append(track)
        
        totalPages = int(XML.ElementFromURL(url).xpath('/lfm/tracks')[0].get('totalPages'))
        morePages = page < totalPages
        return (tracks, morePages)
    
    title = property(getTitle)
    friends = property(getFriends)
    neighbours = property(getNeighbours)
    
    
#########################################################################
class Track:
    def __init__(self, name, artist, url, includeExtendedMetadata=False):
        self.name = name
        self.artist = artist
        self.url = url
        self.includeExtendedMetadata = includeExtendedMetadata
        self.tagCount = None
        self.playCount = None
        self.__canStream = None
        self.__directImage = None
    
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
        if not self.includeExtendedMetadata:
            return None
        else:
            try:
                infoUrl =  TRACK_INFO % (String.Quote(self.artist, True), String.Quote(self.name, True))
                return XML.ElementFromURL(infoUrl)
            except:
                return None
            
        
#########################################################################
class Album:
    def __init__(self, name, artist, includeExtendedMetadata=False):
        self.name = name
        self.artist = artist
        self.includeExtendedMetadata = includeExtendedMetadata
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
        if not self.includeExtendedMetadata:
            return None
        else:
            try:
                infoUrl =  ALBUM_INFO % (String.Quote(self.artist, True), String.Quote(self.name, True))
                return XML.ElementFromURL(infoUrl)
            except:
                return None
            
        
########################################################################################
class Artist:
    def __init__(self, name, includeExtendedMetadata=False):
        self.name = name
        self.includeExtendedMetadata = includeExtendedMetadata
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
        if not self.includeExtendedMetadata:
            return None
        else:
            try:
                infoUrl =  ARTIST_INFO % (String.Quote(self.name, True))
                return XML.ElementFromURL(infoUrl)
            except:
                return None
        
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
    
########################################################################################
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
        