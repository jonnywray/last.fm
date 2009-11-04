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
        
    title = property(getTitle)
    
#########################################################################
class Track:
    def __init__(self, name, artist, url, includeExtendedMetadata=False):
        self.name = name
        self.artist = artist
        self.url = url
        self.includeExtendedMetadata = includeExtendedMetadata
        self.directImage = None
        self.tagCount = None
        self.playCount = None
        self.streamable = False
    
    def getSummary(self):
        trackInfo = self.__trackInfo()
        summary = None
        if trackInfo != None:
            items = trackInfo.xpath('/lfm/track/wiki/summary')
            if len(items) > 0 and items[0].text != None:
                summary = String.StripTags(items[0].text)
        return summary

    def setImage(self, image):
        self.directImage = image
        
    def getImage(self):
        if self.directImage != None:
            return self.directImage
        else:
            trackInfo = self.__trackInfo()
            image = None
            if trackInfo != None:
                items = trackInfo.xpath('/lfm/track/album')
                if len(items) > 0:
                    image = Image(items[0])
            return image
            
    summary = property(getSummary)
    image = property(getImage, setImage)
        
    def __trackInfo(self):
        if not self.includeExtendedMetadata:
            return None
        else:
            infoUrl =  TRACK_INFO % (String.Quote(self.artist, True), String.Quote(self.name, True))
            return XML.ElementFromURL(infoUrl)
        
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
            infoUrl =  ALBUM_INFO % (String.Quote(self.artist, True), String.Quote(self.name, True))
            return XML.ElementFromURL(infoUrl)
        
########################################################################################
class Artist:
    def __init__(self, name, includeExtendedMetadata=False):
        self.name = name
        self.includeExtendedMetadata = includeExtendedMetadata
        self.directImage = None
        
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
            infoUrl =  ARTIST_INFO % (String.Quote(self.name, True))
            return XML.ElementFromURL(infoUrl)
        
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
        