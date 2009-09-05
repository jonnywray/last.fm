import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"

BASE_URL = "http://www.last.fm%s"
PAGED_URL = "http://www.last.fm%s?page=%d"
RADIO_PAGE_URL = "http://www.last.fm/listen/artist%s/similarartists"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(MUSIC_PREFIX, MainMenu, "Last.FM", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.FM'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
def MainMenu():
    dir = MediaContainer(mediaType='music')  
    musicUrl = BASE_URL % "/music"
    for item in XML.ElementFromURL(musicUrl, True).xpath('//div[@class="tagBrowser"]/ul[@class="tagList"]/li/a'):
        title = item.text.capitalize()
        url = item.get('href')
        dir.Append(Function(DirectoryItem(Category, title), path = url))
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

#
# TODO: add videos and similar artists
#
def Artist(sender, name, thumb, path):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    artistUrl = BASE_URL % path
    radioUrl = RADIO_PAGE_URL % path
    title = name + " Radio"
    # TODO: this is odd
    bio = XML.ElementFromURL(artistUrl, True).xpath('//div[@id="wikiAbstract"]')[0].text
    dir.Append(WebVideoItem(radioUrl, title=title, summary=bio, thumb=thumb))
    return dir
