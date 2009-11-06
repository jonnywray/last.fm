

KEY = "d5310352469c2631e5976d0f4a599773"
API_KEY = "&api_key="+KEY
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="

TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY

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
