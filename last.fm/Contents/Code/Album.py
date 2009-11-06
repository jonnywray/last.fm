
KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

ALBUM_INFO = API_BASE + "album.getinfo&artist=%s&album=%s" + API_KEY

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
