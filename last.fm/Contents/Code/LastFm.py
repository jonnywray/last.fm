import string, datetime, Helper
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from LastFmEntities import *


KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

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

        
#########################################################################
def Friends(userName):
    url = USER_FRIENDS % userName
    users = []
    for friend in XML.ElementFromURL(url).xpath('/lfm/friends/user'):
        name = friend.xpath("name")[0].text
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
        name = neighbour.xpath("name")[0].text
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
        name = albumElement.xpath("name")[0].text
        artist = albumElement.xpath("artist/name")[0].text
        tagCount = None
        playCount = None
        if len(albumElement.xpath("tagcount")) > 0:
            tagCount = albumElement.xpath("tagcount")[0].text
        elif len(albumElement.xpath("playcount")) > 0:
            playCount = albumElement.xpath("playcount")[0].text
        image = Image(albumElement)
        
        album = Album(name, artist, includeExtendedMetadata)
        album.image = image
        album.tagCount = tagCount
        album.playCount = playCount
        albums.append(album)
    return albums

##########################################
def LibraryArtists(userName, includeExtendedMetadata):
    url = LIBRARY_ARTISTS % userName
    artists = []
    for artistElement in XML.ElementFromURL(url).xpath('/lfm/artists/artist'):
        name = artistElement.xpath("name")[0].text
        tagCount = None
        playCount = None
        if len(artistElement.xpath("tagcount")) > 0:
            tagCount = artistElement.xpath("tagcount")[0].text
        elif len(artistElement.xpath("playcount")) > 0:
            playCount = artistElement.xpath("playcount")[0].text
        image = Image(artistElement)
        
        artist = Artist(name, includeExtendedMetadata)
        artist.image = image
        artist.tagCount = tagCount
        artist.playCount = playCount
        artists.append(artist)
    return artists

##########################################
def LibraryTracks(userName, page, includeExtendedMetadata):
    url = LIBRARY_TRACKS % (userName, page)
    tracks = []
    for trackElement in XML.ElementFromURL(url).xpath('/lfm/tracks/track'):
        streamable = int(trackElement.xpath("streamable")[0].text)
        name = trackElement.xpath("name")[0].text
        artist = trackElement.xpath("artist/name")[0].text
        trackUrl = trackElement.xpath("url")[0].text.strip() + "?autostart"
        tagCount = None
        playCount = None
        if len(trackElement.xpath("tagcount")) > 0:
            tagCount = trackElement.xpath("tagcount")[0].text
        elif len(trackElement.xpath("playcount")) > 0:
            playCount = trackElement.xpath("playcount")[0].text
            
        track = Track(name, artist, url, includeExtendedMetadata)
        track.streamable = streamable == 1
        track.tagCount = tagCount
        track.playCount = playCount
        tracks.append(track)
    
    totalPages = int(XML.ElementFromURL(url).xpath('/lfm/tracks')[0].get('totalPages'))
    morePages = page < totalPages
    return (tracks, morePages)


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
