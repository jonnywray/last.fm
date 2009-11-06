

KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

LIBRARY_ALBUMS = API_BASE + "library.getalbums&user=%s" + API_KEY
LIBRARY_ARTISTS = API_BASE + "library.getartists&user=%s" + API_KEY
LIBRARY_TRACKS = API_BASE + "library.gettracks&user=%s&page=%d"+ API_KEY

USER_FRIENDS = API_BASE + "user.getfriends&user=%s" + API_KEY
USER_NEIGHBOURS = API_BASE + "user.getneighbours&user=%s" + API_KEY
USER_TOP_ARTISTS = API_BASE + "user.gettopartists&user=%s" + API_KEY
USER_TOP_ALBUMS = API_BASE + "user.gettopalbums&user=%s" + API_KEY
USER_TOP_TAGS = API_BASE + "user.gettoptags&user=%s" + API_KEY
USER_TOP_TRACKS = API_BASE + "user.gettoptracks&user=%s" + API_KEY
USER_RECENT_TRACKS = API_BASE + "user.getrecenttracks&user=%s" + API_KEY
USER_RECENT_STATIONS = API_BASE + "user.getRecentStations&user=%s&limit=%d" + API_KEY + "&api_sig=%s&sk=%s"
USER_LOVED_TRACKS = API_BASE + "user.getlovedtracks&user=%s&page=%d" + API_KEY

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
    
    