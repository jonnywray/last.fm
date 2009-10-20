import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"

BASE_URL = "http://www.last.fm%s"
RADIO_PAGE_URL = "http://www.last.fm/listen/artist/%s/similarartists"
VIDEOS_PAGE = "http://www.last.fm/music/%s/+videos?page=%d"
# API URLs
API_KEY = "&api_key=d5310352469c2631e5976d0f4a599773"
API_BASE = "http://ws.audioscrobbler.com/2.0/?method="
TOP_TAGS = API_BASE + "tag.gettoptags" + API_KEY
TOP_ARTISTS = API_BASE + "tag.gettopartists&tag=%s" + API_KEY
ARTIST_INFO = API_BASE + "artist.getinfo&artist=%s" + API_KEY
SIMILAR_ARTISTS = API_BASE + "artist.getsimilar&artist=%s" + API_KEY
ARTIST_TRACKS = API_BASE + "artist.gettoptracks&artist=%s" + API_KEY
TRACK_INFO = API_BASE + "track.getinfo&artist=%s&track=%s" + API_KEY
SEARCH_TAGS  = API_BASE + "tag.search&tag=%s&page=%d" + API_KEY
SEARCH_ARTISTS = API_BASE + "artist.search&artist=%s&page=%d" + API_KEY
SEARCH_NAMESPACE   = {'opensearch':'http://a9.com/-/spec/opensearch/1.1/'}

DISPLAY_METADATA = "displayMetaData"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"


####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, "Last.fm", ICON, "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.fm'
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
def CreatePrefs():
  Prefs.Add(id=DISPLAY_METADATA, type='bool', default=False, label='Display artist biography and track information (slower navigation)')
##################################
# Search tags
# Search artists
# Charts: seem to be geo based but use country names rather that 2 letter code. Map from code :-> name needed
def MainMenu():
    dir = MediaContainer(mediaType='video') 
    dir.Append(Function(DirectoryItem(TopTags, "Top Tags")))
    dir.Append(Function(InputDirectoryItem(SearchTags, title=L("Search Tags ..."), prompt=L("Search Tags"), thumb=R('search.png'))))
    dir.Append(Function(InputDirectoryItem(SearchArtists, title=L("Search Artists ..."), prompt=L("Search Artists"), thumb=R('search.png'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    
#######################################################################
def SearchTags(sender, query, page=1):
  dir = MediaContainer(title2=sender.itemTitle)
  url = SEARCH_TAGS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/tagmatches/tag'):
    tagName = item.xpath('name')[0].text
    dir.Append(Function(DirectoryItem(CategoryArtists, title=tagName.capitalize()), tag = tagName))
  
  # Pagination
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  if startIndex + itemsPerPage < total:
      dir.Append(Function(DirectoryItem(SearchTags, "More ..."), query = query, page = page+1))
  return dir
  
#######################################################################
def SearchArtists(sender, query, page=1):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  url = SEARCH_ARTISTS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/artistmatches/artist'):
    name = item.xpath('name')[0].text
    image = Image(item)
    summary = ArtistSummary(name)
    dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, summary=summary), artist = name, image=image, summary=summary))
  
  # Pagination
  total = int(content.xpath("/lfm/results/opensearch:totalResults", namespaces=SEARCH_NAMESPACE)[0].text)
  startIndex = int(content.xpath("/lfm/results/opensearch:startIndex", namespaces=SEARCH_NAMESPACE)[0].text)
  itemsPerPage = int(content.xpath("/lfm/results/opensearch:itemsPerPage", namespaces=SEARCH_NAMESPACE)[0].text)
  if startIndex + itemsPerPage < total:
      dir.Append(Function(DirectoryItem(SearchArtists, "More ..."), query = query, page = page+1))
  return dir
  
#######################################################################
def TopTags(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for tagItem in XML.ElementFromURL(TOP_TAGS).xpath('/lfm/toptags/tag'):
        tagName = tagItem.xpath("name")[0].text.strip()
        tagCount = tagItem.xpath("count")[0].text
        subtitle = "Tag Count: " + tagCount
        dir.Append(Function(DirectoryItem(CategoryArtists, title=tagName.capitalize(), subtitle=subtitle), tag = tagName))
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
        image = Image(artist)
        summary = ArtistSummary(name)
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
    streamable = XML.ElementFromURL(ARTIST_INFO % String.Quote(artist)).xpath('/lfm/artist/streamable')[0].text
    if streamable == '1':
        radioUrl = RADIO_PAGE_URL % String.Quote(artist, True)
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
# Playable tracks from the artist.
def ArtistTracks(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = ARTIST_TRACKS % String.Quote(artist, True)
    for track in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        name = track.xpath("name")[0].text
        streamable = track.xpath("streamable")[0].text
        image = Image(track)
        playcount = track.xpath("playcount")[0].text
        url = track.xpath("url")[0].text
        subtitle = "Play count: " + playcount
        infoUrl = None
        summary = TrackSummary(artist, name)
        dir.Append(WebVideoItem(url, title=name, thumb=image, subtitle=subtitle, summary=summary))
    return dir

#######################################################
def SimilarArtists(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = SIMILAR_ARTISTS % String.Quote(artist, True)
    for artist in XML.ElementFromURL(url).xpath('/lfm/similarartists/artist'):
        name = artist.xpath("name")[0].text
        match = artist.xpath("match")[0].text
        subtitle = "Match: " + match + "%"
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, subtitle=subtitle, thumb=image, summary=summary), artist = name, image=image, summary=summary))
    return dir


##########################################
def TrackSummary(artist, name):
    infoUrl = None
    try:
        infoUrl = TRACK_INFO % (String.Quote(artist, True), String.Quote(name, True))
    except:
        pass
    summary = None
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        content = XML.ElementFromURL(infoUrl).xpath('/lfm/track/wiki/summary')
        if len(content) > 0:
            summary = String.StripTags(content[0].text)
    return summary

##########################################
def ArtistSummary(name):
    infoUrl = None
    try:
        infoUrl = ARTIST_INFO % String.Quote(name)
    except:
        pass
    Log(infoUrl)
    summary = None
    if Prefs.Get(DISPLAY_METADATA) and infoUrl != None:
        summaryItems = XML.ElementFromURL(infoUrl).xpath('/lfm/artist/bio/summary')
        if len(summaryItems) > 0:
            summaryItem = summaryItems[0].text
            if summaryItem != None:
                summary = String.StripTags(summaryItem.strip())
    return summary

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