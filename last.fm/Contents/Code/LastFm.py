import string, datetime, Helper
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from LastFmEntities import *

# Dictonary keys
AUTH_KEY = "authentication"
SUBSCRIBE = "subscribe"

SECRET = "95305a7a167653058d921994b58eaf3b"
KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

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

########################################################
def RecommendedArtists(includeExtendedMetadata):    
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
        artist = Artist(name, includeExtendedMetadata)
        artist.image = image
        artists.append(artist)
        
    return artists

#########################################################################
def Friends(userName):
    url = USER_FRIENDS % userName
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
            
#########################################################################
def Neighbours(userName):
    url = USER_NEIGHBOURS % userName
    users = []
    for neighbour in XML.ElementFromURL(url).xpath('/lfm/neighbours/user'):
        name = neighbour.xpath("name")[0].text.strip()
        realName = None
        image = Image(neighbour)
        user = User(name, realName, image)
        users.append(user)
    return users

    
##########################################
def LibraryAlbums(userName, includeExtendedMetadata):
    url = LIBRARY_ALBUMS % userName
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

##########################################
def LibraryArtists(userName, includeExtendedMetadata):
    url = LIBRARY_ARTISTS % userName
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/artists/artist'):
        name = artistElement.xpath("name")[0].text.strip()
        
        artist = Artist(name, includeExtendedMetadata)
        artist.image = Image(artistElement)
        artist.tagCount = TagCount(artistElement)
        artist.playCount = PlayCount(artistElement)
        artists.append(artist)
    return artists

##########################################
def LibraryTracks(userName, page, includeExtendedMetadata):
    url = LIBRARY_TRACKS % (userName, page)
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

##########################################################################
def LovedTracks(userName, page, includeExtendedMetadata):
    url = USER_LOVED_TRACKS % (userName, page)
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


##########################################################################
def RecentTracks(userName, includeExtendedMetadata):
    url = USER_RECENT_TRACKS % userName
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


#######################################################################
def TagArtistChart(tag, includeExtendedMetadata):
    url = TAG_WEEKLY_ARTIST_CHART % tag
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/weeklyartistchart/artist'):
        name = artistElement.xpath("name")[0].text
        artist = Artist(name, includeExtendedMetadata)
        artists.append(artist)
    return artists

#######################################################################
def TagTopArtists(tag):
   url = TAG_TOP_ARTISTS % String.Quote(tag)
   return TopArtists(url)
        
#######################################################################
def TagTopTags():
   url = TAG_TOP_TAGS
   return TopTags(url)

#######################################################################
def TagTopAlbums(tag, includeExtendedMetadata):
   url = TAG_TOP_ALBUMS % String.Quote(tag)
   return TopAlbums(url, includeExtendedMetadata)

#######################################################################
def TagTopTracks(tag, includeExtendedMetadata):
   url = TAG_TOP_TRACKS % String.Quote(tag)
   return TopTracks(url, includeExtendedMetadata)

#######################################################################
def UserTopTags(user):
   url = USER_TOP_TAGS % String.Quote(user)
   return TopTags(url)

#######################################################################
def UserTopArtists(user, includeExtendedMetadata):
   url = USER_TOP_ARTISTS % String.Quote(user)
   return TopArtists(url, includeExtendedMetadata)
    
#######################################################################
def UserTopAlbums(user, includeExtendedMetadata):
   url = USER_TOP_ALBUMS % String.Quote(user)
   return TopAlbums(url, includeExtendedMetadata)

#######################################################################
def UserTopTracks(user, includeExtendedMetadata):
   url = USER_TOP_TRACKS % String.Quote(user)
   return TopTracks(url, includeExtendedMetadata)


#######################################################################
def TopTags(url):
    tags = [] 
    for tagItem in XML.ElementFromURL(url).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        
        tag = Tag(tagName, tagCount)
        tags.append(tag)
    return tags

#######################################################################
def TopArtists(url, includeExtendedMetadata):
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artistElement.xpath("name")[0].text.strip()
           
        artist = Artist(name, includeExtendedMetadata)
        artist.image = Image(artistElement)
        artist.tagCount = TagCount(artistElement)
        artist.playCount = PlayCount(artistElement)
        artists.append(artist)
        
    return artists

##########################################################################
def TopAlbums(url, includeExtendedMetadata):
    albums = []
    for albumElement in XML.ElementFromURL(url).xpath('/lfm/topalbums/album'):
        name = albumElement.xpath("name")[0].text.strip()
        artist = albumElement.xpath("artist/name")[0].text.strip()
         
        album = Album(name, artist, includeExtendedMetadata)
        album.image = Image(albumElement)
        album.tagCount = TagCount(albumElement)
        album.playCount = PlayCount(albumElement)
        albums.append(album)
    return albums

##########################################################################
def TopTracks(url, includeExtendedMetadata):
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        streamable = int(trackElement.xpath("streamable")[0].text.strip())
        name = trackElement.xpath("name")[0].text.strip()
        artist = trackElement.xpath("artist/name")[0].text.strip()
        trackUrl = TrackUrl(trackElement)
        
        track = Track(name, artist, trackUrl, includeExtendedMetadata)
        track.image = Image(trackElement)
        track.streamable = streamable
        track.tagCount = TagCount(trackElement)
        track.playCount = PlayCount(trackElement)
        tracks.append(track)
        
    return tracks

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
    