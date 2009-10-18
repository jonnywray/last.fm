import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"

BASE_URL = "http://www.last.fm%s"
RADIO_PAGE_URL = "http://www.last.fm/listen/artist/%s/similarartists"
# API URLs
API_KEY = "&api_key=d5310352469c2631e5976d0f4a599773"
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="
TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
SIMILAR_ARTISTS = API_BASE + "artist.getsimilar&artist=%s" + API_KEY

VIDEOS_PAGE = "http://www.last.fm/music/%s/+videos?page=%d"

DISPLAY_ARTIST_BIO = "displayBio"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, "last.fm", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'last.fm'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
def CreatePrefs():
  Prefs.Add(id=DISPLAY_ARTIST_BIO, type='bool', default=False, label='Display artist biography (slower navigation)')
##################################
# Video section. How to do navigation?
# 
# Categories/Tags
# Search Tags
# Search Artists
# 
# Category > Artists > Videos: Agrees with Yahoo Music
def MainMenu():
    dir = MediaContainer(viewGroup='Details', mediaType='video') 
    for tagItem in XML.ElementFromURL(TOP_TAGS).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        subtitle = "Tag Count: " + tagCount
        dir.Append(Function(DirectoryItem(CategoryArtists, title=tagName.capitalize(), subtitle=subtitle), tag = tagName))
    dir.Append(PrefsItem(L("Preferences..."), thumb=R('icon-prefs.png')))
    return dir
    
# Add context menus for:
#   getting similar artists
#   'shouting' an artist, if logged in
#   'share an artist', if logged in
#   adding tags
##########################################################################
def CategoryArtists(sender, tag):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = TOP_ARTISTS % (String.Quote(tag, True))
    for artist in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artist.xpath("name")[0].text
        tagCount = artist.xpath("tagcount")[0].text
        subtitle = "Tag Count: " + tagCount
        image = artist.xpath('image[@size="extralarge"]')[0].text
        infoUrl = None
        try:
           infoUrl = ARTIST_INFO % String.Quote(name)
        except:
           pass
        # This adds meta-data but slows things down.
        summary = None
        if Prefs.Get(DISPLAY_ARTIST_BIO) and infoUrl != None:
            summary = String.StripTags(XML.ElementFromURL(infoUrl).xpath('/lfm/artist/bio/summary')[0].text)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir

# For each artist add:
# > Videos
# > Play Radio
# > Tracks
# > Similar Artists > Another artist list
# > Other?
def Artist(sender, artist, image, summary):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(ArtistVideos, title="Videos", thumb=image, summary=summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistTracks, title="Tracks", thumb=image, summary=summary), artist = artist))
    radioUrl = radioUrl = RADIO_PAGE_URL % String.Quote(artist, True)
    dir.Append(WebVideoItem(radioUrl, title= "Play "+artist+" Radio", thumb=image, summary=summary))
    dir.Append(Function(DirectoryItem(SimilarArtists, title="Similar Artists", thumb=image, summary=summary), artist = artist))
    return dir

##########################################################################
# Scraping. Videos aren't covered by the API. 
#  Meta-data is available via track.getinfo
#  Should add scrobling once logged in as well as track loving/sharing
def ArtistVideos(sender, artist, page=1):
    dir = MediaContainer(title2=sender.itemTitle) 
    url = VIDEOS_PAGE % (String.Quote(artist), page)
    for video in XML.ElementFromURL(url, True, errors="ignore").xpath('//ul[@class="clearit videos  mediumVideoList"]/li'):
        title = video.xpath("a/strong")[0].text
        thumb = video.xpath("a//img")[0].get('src')
        path = video.xpath("a")[0].get('href')
        videoUrl = BASE_URL % path
        dir.Append(WebVideoItem(videoUrl, title=title, thumb=thumb))
    if len(XML.ElementFromURL(url, True, errors="ignore").xpath('//a[@class="nextlink"]')) > 0:
        dir.Append(Function(DirectoryItem(ArtistVideos, title="More ..."), artist=artist, page=page+1))
    return dir

#######################################################
#
# Playable tracks from the artist. This may differ based on whether you are logged in or not,
# and subscriptions
#
def ArtistTracks(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    return dir

#######################################################
def SimilarArtists(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = SIMILAR_ARTISTS % String.Quote(artist, True)
    for artist in XML.ElementFromURL(url).xpath('/lfm/similarartists/artist'):
        name = artist.xpath("name")[0].text
        match = artist.xpath("match")[0].text
        subtitle = "Match: " + match + "%"
        image = artist.xpath('image[@size="extralarge"]')[0].text
        infoUrl = None
        try:
           infoUrl = ARTIST_INFO % String.Quote(name)
        except:
           pass
        
        summary = None
        if Prefs.Get(DISPLAY_ARTIST_BIO) and infoUrl != None:
            summary = String.StripTags(XML.ElementFromURL(infoUrl).xpath('/lfm/artist/bio/summary')[0].text)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir
