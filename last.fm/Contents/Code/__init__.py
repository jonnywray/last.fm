import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from LastFm import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"
CACHE_INTERVAL    = 1800

# Two video types - Last.FM and YouTube
VIDEO_PLAY_LIST = "http://ext.last.fm/1.0/video/getplaylist.php?&vid=%s&artist=%s"
YOU_TUBE_PAGE = "http://www.youtube.com/watch?v=%s" 

# Context menu map keys
NAME = "name"
ARTIST = "artist"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, "Last.fm", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.fm'
  DirectoryItem.thumb=R("icon-default.png")
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
####################################################################################################
def CreatePrefs():
  Prefs.Add(id=LastFm.DISPLAY_METADATA, type='bool', default=False, label='Display detailed track, artist and album data (slower navigation)')
  Prefs.Add(id=LastFm.LOGIN_PREF_KEY,    type='text', default=None, label='Login')
  Prefs.Add(id=LastFm.PASSWD_PREF_KEY, type='text', default=None, label='Password', option='hidden')
  
##################################
def MainMenu():
    Authenticate()
    dir = MediaContainer(mediaType='video') 
    if LastFm.IsAuthenticated():
        user = LastFm.CurrentUser()
        dir.Append(Function(DirectoryItem(Library, "Library"), user = user))
        dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks"), user = user))
        dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks"), user = user))
        
      #  if Dict.Get(SUBSCRIBE) == '1':
      #      dir.Append(Function(DirectoryItem(RecentStations, "Recent Stations", thumb=R(ICON)), userName = Prefs.Get(LOGIN_PREF_KEY)))
        dir.Append(Function(DirectoryItem(RecommendedArtists, "Recommended Artists")))
        
        dir.Append(Function(DirectoryItem(UserTopArtists, "Top Artists"), user = user))
        dir.Append(Function(DirectoryItem(UserTopAlbums, "Top Albums"), user = user))
        dir.Append(Function(DirectoryItem(UserTopTracks, "Top Tracks"), user = user))
        dir.Append(Function(DirectoryItem(TagTopTags, "Top Tags")))
        dir.Append(Function(DirectoryItem(Friends, "Friends"), user = user))
        dir.Append(Function(DirectoryItem(Neighbours, "Neighbors"), user = user))
    
    dir.Append(Function(InputDirectoryItem(SearchAlbumsResults, title="Search Albums ...", prompt="Search Albums", thumb=S('Search'))))
    dir.Append(Function(InputDirectoryItem(SearchArtistsResults, title="Search Artists ...", prompt="Search Artists", thumb=S('Search'))))
    dir.Append(Function(InputDirectoryItem(SearchTagsResults, title="Search Tags ...", prompt="Search Tags", thumb=S('Search'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    
########################################################
def Friends(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    for friend in user.friends:
        dir.Append(Function(DirectoryItem(UserDirectory, title=friend.title, thumb=friend.image), user = friend))
    return dir

########################################################
def Neighbours(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    for neighbour in user.neighbours:
        dir.Append(Function(DirectoryItem(UserDirectory, title=neighbour.title, thumb=neighbour.image), user = neighbour))
    return dir

########################################################
def UserDirectory(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
   
    dir.Append(Function(DirectoryItem(Library, "Library"), user = user))
    dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks"), user = user))
    dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks"), user = user))
    #if Dict.Get(SUBSCRIBE) == '1':
    #    dir.Append(Function(DirectoryItem(RecentStations, "Recent Stations", thumb=R(ICON)), userName = name))
    dir.Append(Function(DirectoryItem(UserTopArtists, "Top Artists"), user = user.name))
    dir.Append(Function(DirectoryItem(UserTopAlbums, "Top Albums"), user = user.name))
    dir.Append(Function(DirectoryItem(UserTopTracks, "Top Tracks"), user = user.name))
    dir.Append(Function(DirectoryItem(UserTopTags, "Top Tags"), user = user.name))
    dir.Append(Function(DirectoryItem(Friends, "Friends"), user = user))
    dir.Append(Function(DirectoryItem(Neighbours, "Neighbors"), user = user))
    return dir


########################################################
def Library(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(LibraryAlbums, "Albums"), user = user))
    dir.Append(Function(DirectoryItem(LibraryArtists, "Artists"), user = user))
    dir.Append(Function(DirectoryItem(LibraryTracks, "Tracks"), user = user))
    return dir

########################################################
def LibraryAlbums(sender, user ): 
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for album in user.libraryAlbums:
        title = album.name + " - " + album.artist
        subtitle = str(album.plays) +" plays ("+ str(album.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary), album = album))
    return dir

########################################################
def LibraryArtists(sender, user):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for artist in user.libraryArtists:
        subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary), artist = artist))
    return dir

########################################################
def LibraryTracks(sender, user, page=1):
    menu = ContextMenu(includeStandardItems=False)
    #menu.Append(Function(DirectoryItem(LoveTrack, title="Love Track")))
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu)
    tracksTuple = user.getLibraryTracks(page)
    for track in tracksTuple[0]:
       AppendTrack(dir, track)
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LibraryTracks, "More ..."), user = user, page = page+1))
    return dir

########################################################
def RecommendedArtists(sender):    
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
    for artist in LastFm.RecommendedArtists():
        subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, thumb=artist.image, subtitle=subtitle, summary=artist.summary), artist = artist))
    return dir
  
##########################################################################
def LovedTracks(sender, user, page=1):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    tracksTuple = user.getLovedTracks(page)
    for track in tracksTuple[0]:
        AppendTrack(dir, track)
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LovedTracks, "More ..."), user = user, page = page+1))
    return dir

##########################################################################
def RecentTracks(sender, user):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for track in user.recentTracks:
        AppendTrack(dir, track)
    return dir

#######################################################################
def Category(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(TagTopArtists, "Top Artists"), tag = tag))
    dir.Append(Function(DirectoryItem(TagTopAlbums, "Top Albums"), tag = tag))
    dir.Append(Function(DirectoryItem(TagTopTracks, "Top Tracks"), tag = tag))
    dir.Append(Function(DirectoryItem(ArtistChart, "Weekly Artist Chart"), tag=tag))
    dir.Append(Function(DirectoryItem(SimilarTags, "Similar Tags"), tag=tag))
    return dir

#######################################################################
def ArtistChart(sender, tag):
    dir = MediaContainer(viewGroup='Details',title2=sender.itemTitle) 
    for artist in tag.artistChart:
        subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary), artist = artist))
    return dir

#######################################################################
def TagTopTags(sender):
    return TopTags(sender, LastFm.TagTopTags())

#######################################################################
def UserTopTags(sender, user):
    return TopTags(sender, user.topTags)

#######################################################################
def TagTopArtists(sender, tag):
    return TopArtists(sender, tag.topArtists)

#######################################################################
def UserTopArtists(sender, user):
    return TopArtists(sender, user.topArtists)

##########################################################################
def TagTopAlbums(sender, tag):
    return TopAlbums(sender, tag.topAlbums)
    
##########################################################################
def UserTopAlbums(sender, user):
    return TopAlbums(sender, user.topAlbums)

##########################################################################
def TagTopTracks(sender, tag):
    return TopTracks(sender, tag.topTracks)

##########################################################################
def UserTopTracks(sender, user):
    return TopTracks(sender, user.topTracks)

##########################################################################
def TopArtists(sender, artists):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for artist in artists:
        subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary), artist = artist))
    return dir

##########################################################################
def TopAlbums(sender, albums):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for album in albums:
        title = album.name + " - " + album.artist
        subtitle = str(album.plays) +" plays ("+ str(album.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary), album=album))
    return dir

##########################################################################
def TopTracks(sender, tracks):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for track in tracks:
        AppendTrack(dir, track)
    return dir

#######################################################################
def TopTags(sender, tags):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for tag in tags:
        subtitle = "Tag Count: " + tag.tagCount
        dir.Append(Function(DirectoryItem(Category, title=tag.name.capitalize(), subtitle=subtitle), tag = tag))
    return dir

############################################################################
def ArtistDirectory(sender, artist):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(ArtistVideos, title="Videos", thumb=artist.image, summary=artist.summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistTracks, title="Tracks", thumb=artist.image, summary=artist.summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistAlbums, title="Albums", thumb=artist.image, summary=artist.summary), artist = artist))
    # TODO: this will change for people with pay accounts
    if artist.streamable:
        title = "Play "+artist.name+" Radio"
        dir.Append(WebVideoItem(artist.radioUrl, title=title, thumb=artist.image, summary=artist.summary))
    dir.Append(Function(DirectoryItem(SimilarArtists, title="Similar Artists", thumb=artist.image, summary=artist.summary), artist = artist))
    return dir

############################################################################
def AlbumDirectory(sender, album):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for track in album.trackList:
        AppendTrack(dir, track)
    return dir


############################################################################
def AppendTrack(dir, track):
    title=track.name + " - " + track.artist
    url = track.url
    subtitle = str(track.plays) +" plays ("+ str(track.listeners) + " listeners)"
    if not track.streamable:
        subtitle = subtitle + "\nNot Streamable"
        url = "garbage"
    dir.Append(WebVideoItem(url, title=title, subtitle=subtitle, thumb=track.image, summary=track.summary, contextKey=title, contextArgs={NAME:track.name, ARTIST:track.artist}))

##########################################################################
def CountSubTitle(obj):
    subtitle = ""
    if obj.tagCount != None and obj.tagCount > 0:
        subtitle = "Tag Count: " + str(obj.tagCount) + "\n"
    elif obj.playCount != None and obj.playCount > 0:
        subtitle = "Play Count: " + str(obj.playCount) + "\n"
    return subtitle

#######################################################
def ArtistAlbums(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for album in artist.albums:
        title = album.name + " - " + album.artist
        subtitle = str(album.plays) +" plays ("+ str(album.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary), album=album))
    return dir

#######################################################
def ArtistTracks(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for track in artist.tracks:
        AppendTrack(dir, track)
    return dir

##########################################################################
def SimilarTags(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    for tag in tag.similarTags:
        dir.Append(Function(DirectoryItem(Category, title=tag.name.capitalize()), tag = tag))
    return dir

#######################################################
def SimilarArtists(sender, artist):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    for artist in artist.similarArtists:
        subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
        dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary), artist = artist))
    return dir


#######################################################################
def SearchTagsResults(sender, query, page=1):
  dir = MediaContainer(title2=sender.itemTitle)
  results = LastFm.SearchTags(query, page)
  for tag in results[0]:
    dir.Append(Function(DirectoryItem(Category, title=tag.name.capitalize()), tag = tag))
  if results[1]:
      dir.Append(Function(DirectoryItem(SearchTagsResults, "More ..."), query = query, page = page+1))
  return dir
  
#######################################################################
def SearchArtistsResults(sender, query, page=1):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  results = LastFm.SearchArtists(query, page)
  for artist in results[0]:
    dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, thumb=artist.image, summary=artist.summary), artist = artist))
  if results[1]:
     dir.Append(Function(DirectoryItem(SearchArtistsResults, "More ..."), query = query, page = page+1))
  return dir
  
#######################################################################
def SearchAlbumsResults(sender, query, page=1):
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle)
  results = LastFm.SearchAlbums(query, page)
  for album in results[0]:
     title = album.name + " - " + album.artist
     subtitle = str(album.plays) +" plays ("+ str(album.listeners) + " listeners)"
     dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary), album=album))
  if results[1]:
      dir.Append(Function(DirectoryItem(SearchAlbumsResults, "More ..."), query = query, page = page+1))
  return dir
  
##########################################################################
# Some are Last.FM whereas some are from YouTube. I haven't seen other places
def ArtistVideos(sender, artist, page=1):
    dir = MediaContainer(title2=sender.itemTitle) 
    videos = artist.getVideos(page)
    for video in videos[0]:
        if(video.isYouTube()):
           dir.Append(Function(VideoItem(YouTubeVideo, title=video.title, thumb=video.thumb), video=video))
        else:
           dir.Append(Function(VideoItem(LastFmVideo, title=video.title, thumb=video.thumb), video=video, artist=artist))
    if videos[1]:
        dir.Append(Function(DirectoryItem(ArtistVideos, title="More ..."), artist=artist, page=page+1))
    return dir
    
############################################
def LastFmVideo(sender, video, artist):
    playList = HTTP.Request(VIDEO_PLAY_LIST % (video.videoId, String.Quote(artist.name, True)))
    start = playList.index('<location>') + 10
    stop = playList.index('</location>')
    videoUrl = playList[start:stop]
    return Redirect(videoUrl)
    
############################################
# A little borrowing from the YouTube plugin here. Thanks.
def YouTubeVideo(sender, video):
    ytPage = HTTP.Request(YOU_TUBE_PAGE % video.videoId)
    t = re.findall('"t": "([^"]+)"', ytPage)[0]
    v = re.findall("'VIDEO_ID': '([^']+)'", ytPage)[0] #
    hd = re.findall("'IS_HD_AVAILABLE': ([^,]+),", ytPage)[0] #
    
    fmt = "18"
    if hd == "true":
      fmt = "22"
      
    videoUrl = "http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%s" % (v, t, fmt)
    return Redirect(videoUrl)

