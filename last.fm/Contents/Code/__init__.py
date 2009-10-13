import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"

BASE_URL = "http://www.last.fm%s"
PAGED_URL = "http://www.last.fm%s?page=%d"

API_KEY = "&api_key=d5310352469c2631e5976d0f4a599773"
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="
TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
VIDEOS_PAGE = "http://www.last.fm/music/%s/+videos?page=%d"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, "Last.FM Videos", ICON, "art-default.png")
  Plugin.AddPrefixHandler(MUSIC_PREFIX, MusicMainMenu, "Last.FM", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.FM'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
##################################
# Video section. How to do navigation?
# 
# Category > Artists > Videos: Agrees with Yahoo Music
# Category > Videos
def VideoMainMenu():
    dir = MediaContainer(viewGroup='Details', mediaType='video') 
    for tagItem in XML.ElementFromURL(TOP_TAGS).xpath('/lfm/toptags/tag'):
        tag = tagItem.xpath("name")[0].text
        name = tag.capitalize()
        tagCount = tagItem.xpath("count")[0].text
        subtitle = "Tag Count: "+tagCount
        dir.Append(Function(DirectoryItem(CategoryArtists, title=name, subtitle=subtitle), tag = tag))
    return dir
    
##########################################################################
def CategoryArtists(sender, tag):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = TOP_ARTISTS % (tag)
    for artist in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artist.xpath("name")[0].text
        tagCount = artist.xpath("tagcount")[0].text
        image = artist.xpath('image[@size="extralarge"]')[0].text
        subtitle = "Tag Count: "+tagCount
        infoUrl = ARTIST_INFO % String.Quote(name)
        # This adds meta-data but slows things down.
        summary = String.StripTags(XML.ElementFromURL(infoUrl).xpath('/lfm/artist/bio/summary')[0].text)
        dir.Append(Function(DirectoryItem(ArtistsVideos, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name))
    
    return dir

##########################################################################
# Scraping. Videos aren't covered by the API
def ArtistsVideos(sender, artist, page=1):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = VIDEOS_PAGE % (String.Quote(artist), page)
    for video in XML.ElementFromURL(url, True, errors="ignore").xpath('//ul[@class="clearit videos  mediumVideoList"]/li'):
        title = video.xpath("a/strong")[0].text
        thumb = video.xpath("a//img")[0].get('src')
        path = video.xpath("a")[0].get('href')
        Log(title+":"+url)
        videoUrl = BASE_URL % path
        dir.Append(WebVideoItem(videoUrl, title=title, thumb=thumb))
    return dir


####################################
# Music section
def MusicMainMenu():
    dir = MediaContainer(mediaType='music')  
    musicUrl = BASE_URL % "/music"
    for item in XML.ElementFromURL(musicUrl, True).xpath('//div[@class="tagBrowser"]/ul[@class="tagList"]/li/a'):
        title = item.text.capitalize()
        url = item.get('href')
        dir.Append(Function(DirectoryItem(Category, title), tag = url))
    return dir

def Category(sender, path, page=1):
    dir = MediaContainer(mediaType='music', title2=sender.itemTitle) 
    categoryUrl = PAGED_URL % (path, page)
    for item in XML.ElementFromURL(categoryUrl, True).xpath('//ul[@class="artistList"]/li'):
        title = item.xpath("a/strong")[0].text
        thumb = item.xpath("a//img")[0].get('src')
        url = item.xpath("a")[0].get('href')
        dir.Append(Function(DirectoryItem(Artist, title, thumb=thumb), name = title, path = url, thumb=thumb))
    # TODO: pagination of category items
    return dir
###
def Artist(sender, name, thumb, path):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    artistUrl = BASE_URL % path
    radioUrl = RADIO_PAGE_URL % path
    title = name + " Radio"
    # TODO: this is odd
    bio = XML.ElementFromURL(artistUrl, True).xpath('//div[@id="wikiAbstract"]')[0].text
    dir.Append(WebVideoItem(radioUrl, title=title, summary=bio, thumb=thumb))
    return dir
