
SECRET = "95305a7a167653058d921994b58eaf3b"
KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

TAG_TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TAG_TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
TAG_TOP_ALBUMS = API_BASE + "tag.gettopalbums&tag=%s" + API_KEY
TAG_TOP_TRACKS = API_BASE + "tag.gettoptracks&tag=%s" + API_KEY
TAG_SIMILAR_TAG = API_BASE + "tag.getsimilar&tag=%s" + API_KEY
TAG_WEEKLY_ARTIST_CHART = API_BASE + "tag.getweeklyartistchart&tag=%s" + API_KEY

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
    
def TagTopTags():
    return TopTags(TAG_TOP_TAGS)    

#######################################################################
def TopTags(url):
    tags = [] 
    for tagItem in XML.ElementFromURL(url).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        
        tag = Tag(tagName, tagCount)
        tags.append(tag)
    return tags
