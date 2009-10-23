import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"

BASE_URL = "http://www.last.fm%s"
# Radio playing works, but it is a blank screen (1x1 flash)
RADIO_PAGE_URL = "http://www.last.fm/listen/artist/%s/similarartists"
# Two video types - Last.FM and YouTube
VIDEOS_PAGE = "http://www.last.fm/music/%s/+videos?page=%d"
VIDEO_PLAY_LIST = "http://ext.last.fm/1.0/video/getplaylist.php?&vid=%s&artist=%s"
YOU_TUBE_PAGE = "http://www.youtube.com/watch?v=%s" 

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
TOP_ARTISTS_CHART = API_BASE + "geo.gettopartists&country=%s" + API_KEY
TOP_TRACKS_CHART = API_BASE + "geo.gettoptracks&country=%s" + API_KEY

DISPLAY_METADATA = "displayMetaData"
CACHE_INTERVAL    = 1800
ICON = "icon-default.png"

# Authenticated ideas:
#   'shouting' an artist (context menu)
#   'share' an artist and track (context menu)
#   'love' and 'ban' a track (context menu)
#   adding tags (context menu)
#   playlist support by displaying and adding tracks
#   all user level charts, friends, etc
#   add scrobbling when playing a track or video 

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
# TODO: Charts: seem to be geo based but use country names rather that 2 letter code. Map from code :-> name needed
def MainMenu():
    dir = MediaContainer(mediaType='video') 
    dir.Append(Function(DirectoryItem(TopArtistChart, "Top Artists")))
    dir.Append(Function(DirectoryItem(TopTracksChart, "Top Tracks")))
    dir.Append(Function(DirectoryItem(TopTags, "Top Tags")))
    dir.Append(Function(InputDirectoryItem(SearchTags, title=L("Search Tags ..."), prompt=L("Search Tags"), thumb=R('search.png'))))
    dir.Append(Function(InputDirectoryItem(SearchArtists, title=L("Search Artists ..."), prompt=L("Search Artists"), thumb=R('search.png'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    
########################################################
def TopArtistChart(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    country = "united states"
    url = TOP_ARTISTS_CHART % (String.Quote(country, True))
    for artist in XML.ElementFromURL(url).xpath('/lfm/topartists/artist'):
        name = artist.xpath("name")[0].text
        playcount = artist.xpath("playcount")[0].text
        subtitle = "Play count: " + playcount
        image = Image(artist)
        summary = ArtistSummary(name)
        dir.Append(Function(DirectoryItem(Artist, title=name, thumb=image, subtitle=subtitle, summary=summary), artist = name, image=image, summary=summary))
    return dir
    
########################################################
def TopTracksChart(sender):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    country = "united states"
    url = TOP_TRACKS_CHART % (String.Quote(country, True))
    for track in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        name = track.xpath("name")[0].text
        streamable = track.xpath("streamable")[0].text
        if streamable == "1":
            image = Image(track)
            playcount = track.xpath("playcount")[0].text
            url = track.xpath("url")[0].text + "?autostart"
            subtitle = "Play count: " + playcount
            infoUrl = None
            artist = track.xpath('artist/name')[0].text
            summary = TrackSummary(artist, name)
            dir.Append(WebVideoItem(url, title=artist+" - "+name, thumb=image, subtitle=subtitle, summary=summary))
    return dir

#######################################################################
def SearchTags(sender, query, page=1):
  dir = MediaContainer(title2=sender.itemTitle)
  url = SEARCH_TAGS % (String.Quote(query, True), page)
  content = XML.ElementFromURL(url)
  for item in content.xpath('/lfm/results/tagmatches/tag'):
    tagName = item.xpath('name')[0].text
    dir.Append(Function(DirectoryItem(CategoryArtists, title=tagName.capitalize()), tag = tagName))
  
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

############################################################################
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
# Scraping. Videos aren't covered by the API. Also, some are from
# Last.FM whereas some are from YouTube. I haven't seen other places
def ArtistVideos(sender, artist, page=1):
    dir = MediaContainer(title2=sender.itemTitle) 
    url = VIDEOS_PAGE % (String.Quote(artist), page)
    for video in XML.ElementFromURL(url, True, errors="ignore").xpath('//ul[@class="clearit videos  mediumVideoList"]/li'):
        title = video.xpath("a/strong")[0].text
        thumb = video.xpath("a//img")[0].get('src')
        path = video.xpath("a")[0].get('href')
        videoUrl = BASE_URL % path
        youTube = (thumb.find('youtube.com') > -1) or (thumb.find('ytimg.com') > -1)
        if(youTube):
           videoId = videoUrl.split('/')[-1].replace('+1-','')
           dir.Append(Function(VideoItem(YouTubeVideo, title=title, thumb=thumb), videoId=videoId))
        else:
           videoId = videoUrl.split('/')[-1]
           dir.Append(Function(VideoItem(LastFmVideo, title=title, thumb=thumb), videoId=videoId, artist=artist))
    if len(XML.ElementFromURL(url, True, errors="ignore").xpath('//a[@class="nextlink"]')) > 0:
        dir.Append(Function(DirectoryItem(ArtistVideos, title="More ..."), artist=artist, page=page+1))
    return dir

#######################################################
def ArtistTracks(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    url = ARTIST_TRACKS % String.Quote(artist, True)
    for track in XML.ElementFromURL(url).xpath('/lfm/toptracks/track'):
        name = track.xpath("name")[0].text
        streamable = track.xpath("streamable")[0].text
        if streamable == "1":
          image = Image(track)
          playcount = track.xpath("playcount")[0].text
          url = track.xpath("url")[0].text + "?autostart"
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

############################################
def LastFmVideo(sender, videoId, artist):
    playList = HTTP.Request(VIDEO_PLAY_LIST % (videoId, String.Quote(artist, True)))
    start = playList.index('<location>') + 10
    stop = playList.index('</location>')
    videoUrl = playList[start:stop]
    return Redirect(videoUrl)
    
############################################
# A little borrowing from the YouTube plugin here. Thanks.
def YouTubeVideo(sender, videoId):
    ytPage = HTTP.Request(YOU_TUBE_PAGE % videoId)
    t = re.findall('"t": "([^"]+)"', ytPage)[0]
    v = re.findall("'VIDEO_ID': '([^']+)'", ytPage)[0] #
    hd = re.findall("'IS_HD_AVAILABLE': ([^,]+),", ytPage)[0] #
    
    fmt = "18"
    if hd == "true":
      fmt = "22"
      
    videoUrl = "http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%s" % (v, t, fmt)
    return Redirect(videoUrl)