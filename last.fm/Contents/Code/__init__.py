import re, string, datetime, LastFm
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

MUSIC_PREFIX      = "/music/lastfm"
CACHE_INTERVAL    = 1800

# Two video types - Last.FM and YouTube
VIDEO_PLAY_LIST = "http://ext.last.fm/1.0/video/getplaylist.php?&vid=%s&artist=%s"
YOU_TUBE_PAGE = "http://www.youtube.com/watch?v=%s" 

# Context menu map keys
ITEM = "item"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(MUSIC_PREFIX, MainMenu, "Last.fm", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.art = R('art-default.png')
  MediaContainer.title1 = 'Last.fm'
  DirectoryItem.thumb=R("icon-default.png")
  HTTP.SetCacheTime(CACHE_INTERVAL)
  
####################################################################################################
def CreatePrefs():
  Prefs.Add(id=LastFm.LOGIN_PREF_KEY,    type='text', default=None, label='Login')
  Prefs.Add(id=LastFm.PASSWD_PREF_KEY, type='text', default=None, label='Password', option='hidden')
  
def ValidatePrefs():
    LastFm.Authenticate()
    
##################################
def MainMenu():
    dir = MediaContainer(mediaType='music', noCache=True) 
    if LastFm.IsAuthenticated():
        user = LastFm.CurrentUser()
        if LastFm.IsSubscriber():
            dir.Append(Function(DirectoryItem(Radios, "Radios"), user = user))
        dir.Append(Function(DirectoryItem(Library, "Library"), user = user))
        dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks"), user = user))
        dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks"), user = user))
        dir.Append(Function(DirectoryItem(RecommendedArtists, "Recommended Artists")))
        dir.Append(Function(DirectoryItem(Friends, "Friends"), user = user))
        dir.Append(Function(DirectoryItem(Neighbours, "Neighbours"), user = user))
        
        dir.Append(Function(DirectoryItem(GlobalTopTags, "Top Tags")))
    
        dir.Append(Function(InputDirectoryItem(SearchTagsResults, title="Search Tags ...", prompt="Search Tags", thumb=S('Search'))))
        dir.Append(Function(InputDirectoryItem(SearchArtistsResults, title="Search Artists ...", prompt="Search Artists", thumb=S('Search'))))
        dir.Append(Function(InputDirectoryItem(SearchAlbumsResults, title="Search Albums ...", prompt="Search Albums", thumb=S('Search'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    
#######################################################################
def SearchTagsResults(sender, query, page=1):
  dir = MediaContainer(title2=sender.itemTitle)
  results = LastFm.SearchTags(query, page)
  for tag in results[0]:
      dir.Append(Function(DirectoryItem(Category, title=tag[0].capitalize()), tag = tag))
  if results[1]:
      dir.Append(Function(DirectoryItem(SearchTagsResults, "More ..."), query = query, page = page+1))
  return dir
  
#######################################################################
def SearchArtistsResults(sender, query, page=1):
    results = LastFm.SearchArtists(query, page)
    dir = AppendArtists(sender, results[0])
    if results[1]:
        dir.Append(Function(DirectoryItem(SearchArtistsResults, "More ..."), query = query, page = page+1))
    return dir
  
#######################################################################
def SearchAlbumsResults(sender, query, page=1): 
  results = LastFm.SearchAlbums(query, page)
  dir = AppendAlbums(sender, results[0])
  if results[1]:
      dir.Append(Function(DirectoryItem(SearchAlbumsResults, "More ..."), query = query, page = page+1))
  return dir
    
########################################################
def Friends(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    friends = LastFm.Friends(user)
    for friend in friends:
        name = friend[0]
        if friend[1] != None:
            name = friend[1]
        dir.Append(Function(DirectoryItem(UserDirectory, title=name, thumb=friend[2]), user = friend[0]))
    return dir

########################################################
def Neighbours(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    neighbours = LastFm.Neighbours(user)
    for neighbour in neighbours:
        name = neighbour[0]
        if neighbour[1] != None:
            name = neighbour[1]
        dir.Append(Function(DirectoryItem(UserDirectory, title=name, thumb=neighbour[2]), user = neighbour[0]))
    return dir

########################################################
def UserDirectory(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
   
    dir.Append(Function(DirectoryItem(Radios, "Radios"), user = user))
    dir.Append(Function(DirectoryItem(Library, "Library"), user = user))
    dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks"), user = user))
    dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks"), user = user))
    dir.Append(Function(DirectoryItem(Friends, "Friends"), user = user))
    dir.Append(Function(DirectoryItem(Neighbours, "Neighbours"), user = user))
    return dir

########################################################
def Radios(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    name = None
    if LastFm.IsCurrentUser(user):
        name = "your"
    else:
        userName = LastFm.UserDetails(user)[0]
        name = user+"'s"
        if userName != None:
            name = userName+"'s"
        
    libraryRadio = "user/%s/library" % user
    dir.Append(Function(DirectoryItem(PlayRadio, "Play "+name+" Library Radio"), radioName=libraryRadio))
    lovedRadio = "user/%s/loved" % user
    dir.Append(Function(DirectoryItem(PlayRadio, "Play "+name+" Loved Tracks Radio"), radioName=lovedRadio))
    recommendedRadio = "user/%s/recommended" % user
    dir.Append(Function(DirectoryItem(PlayRadio, "Play "+name+" Recommendations Radio"), radioName=recommendedRadio))
    neighoursRadio = "user/%s/neighbours" % user
    dir.Append(Function(DirectoryItem(PlayRadio, "Play "+name+" Neighbourhood Radio"), radioName=neighoursRadio))
    return dir
    
    
########################################################
def RecommendedArtists(sender):    
    return AppendArtists(sender, LastFm.RecommendedArtists())
    
########################################################
def Library(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    if LastFm.IsSubscriber():
        title = None
        if LastFm.IsCurrentUser(user):
            title = "Play your Library"
        else:
            userName = LastFm.UserDetails(user)[0]
            title = "Play "+user+"'s Library"
            if userName != None:
                title = "Play "+userName+"'s Library"
        radioName = "user/%s/library" % user
        dir.Append(Function(DirectoryItem(PlayRadio, title), radioName=radioName))
    dir.Append(Function(DirectoryItem(LibraryAlbums, "Albums"), user = user))
    dir.Append(Function(DirectoryItem(LibraryArtists, "Artists"), user = user))
    dir.Append(Function(DirectoryItem(LibraryTracks, "Tracks"), user = user))
    return dir

########################################################
def LibraryAlbums(sender, user ): 
    libraryAlbums = LastFm.LibraryAlbums(user)
    return AppendAlbums(sender, libraryAlbums)

########################################################
def LibraryArtists(sender, user):
    libraryArtists = LastFm.LibraryArtists(user)
    return AppendArtists(sender, libraryArtists)

########################################################
def LibraryTracks(sender, user, page=1):    
    tracksTuple = LastFm.LibraryTracks(user, page)
    dir = AppendTracks(sender, tracksTuple[0])
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LibraryTracks, "More ..."), user = user, page = page+1))
    return dir

##########################################################################
def LovedTracks(sender, user, page=1):
    tracksTuple = LastFm.LovedTracks(user, page)
    dir = AppendTracks(sender, tracksTuple[0])
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LovedTracks, "More ..."), user = user, page = page+1))
    return dir

##########################################################################
def RecentTracks(sender, user):
    recentTracks = LastFm.RecentTracks(user)
    return AppendTracks(sender, recentTracks)

########################################################
def GlobalTopTags(sender):
    return TagList(sender, LastFm.GlobalTopTags())

#######################################################################
def TagTopArtists(sender, tag):
    return AppendArtists(sender, LastFm.TagTopArtists(tag[0]))

##########################################################################
def TagTopAlbums(sender, tag):
    return AppendAlbums(sender, LastFm.TagTopAlbums(tag[0]))

##########################################################################
def TagTopTracks(sender, tag):
    return AppendTracks(sender, LastFm.TagTopTracks(tag[0]))

#######################################################################
def TagList(sender, tags):
    dir = MediaContainer(title2=sender.itemTitle) 
    for tag in tags:
        dir.Append(Function(DirectoryItem(Category, title=tag[0].capitalize()), tag = tag))
    return dir

#######################################################
def SimilarArtists(sender, artist):
    similarArtists = LastFm.SimilarArtists(artist[0])
    return AppendArtists(sender, similarArtists)

########################################################
def AppendArtists(sender, artists):
    dir = MediaContainer(title2=sender.itemTitle)
    for artist in artists:
        dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist[0], thumb=artist[1]), artist = artist))
    return dir

########################################################
def AppendAlbums(sender, albums):
    dir = MediaContainer(title2=sender.itemTitle) 
    for album in albums:
        title = album[0] + " - " + album[1]
        dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, thumb=album[2]), album = album))
    return dir

############################################################################
def AlbumDirectory(sender, album):
    trackList = LastFm.AlbumTrackList(album[1], album[0])
    return AppendTracks(sender, trackList)

############################################################################
def AppendTracks(sender, tracks):
    dir = MediaContainer(title2=sender.itemTitle) 
    for track in tracks:
        WebTrack(dir, track)
    return dir

#######################################################
def ArtistAlbums(sender, artist):
    artistAlbums = LastFm.ArtistAlbums(artist[0])
    return AppendAlbums(sender, artistAlbums)

#######################################################
def ArtistTracks(sender, artist):
    artistTracks = LastFm.ArtistTracks(artist[0])
    return AppendTracks(sender, artistTracks)

############################################################################
def ArtistDirectory(sender, artist):
    dir = MediaContainer(title2=sender.itemTitle) 
    radioTitle = "Play "+artist[0]+" Radio"
    if LastFm.IsSubscriber():
        radioName = "artist/%s/similarartists" % String.Quote(artist[0], True)
        dir.Append(Function(DirectoryItem(PlayRadio, radioTitle, thumb=artist[1]), radioName=radioName))
    dir.Append(Function(DirectoryItem(SimilarArtists, title="Similar Artists", thumb=artist[1]), artist = artist))
    dir.Append(Function(DirectoryItem(Videos, title="Videos", thumb=artist[1], summary=None), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistTracks, title="Tracks", thumb=artist[1], summary=None), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistAlbums, title="Albums", thumb=artist[1], summary=None), artist = artist))
    return dir

#######################################################################
def Category(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    radioTitle = "Play " + tag[0].capitalize() + " Radio"
    if LastFm.IsSubscriber():
        radioName = "globaltags/%s" % String.Quote(tag[0], True)
        dir.Append(Function(DirectoryItem(PlayRadio, radioTitle), radioName=radioName))
        
    dir.Append(Function(DirectoryItem(TagTopArtists, "Top Artists"), tag = tag))
    dir.Append(Function(DirectoryItem(TagTopAlbums, "Top Albums"), tag = tag))
    dir.Append(Function(DirectoryItem(TagTopTracks, "Top Tracks"), tag = tag))
    dir.Append(Function(DirectoryItem(SimilarTags, "Similar Tags"), tag=tag))
    return dir


##########################################################################
def SimilarTags(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    for similarTag in LastFm.SimilarTags(tag):
        dir.Append(Function(DirectoryItem(Category, title=similarTag[0].capitalize()), tag = similarTag))
    return dir

#######################################################################
# TODO: real semantics of the radio with refreshing track list is needed here
def PlayRadio(sender, radioName):
    if not Dict.HasKey(radioName):
        newRadio = LastFm.Radio(radioName)
        Dict.Set(radioName, newRadio)
    radio = Dict.Get(radioName)
    dir = MediaContainer(title2=sender.itemTitle, noCache=True) 
    
    track = radio.nextTrack()
    title = track[0] + " - " + track[1]
    image = track[2]
    location = track[3]
    duration = track[4]
    dir.Append(TrackItem(location, title=title, subtitle=None, thumb=image, duration=duration))  
    return dir

############################################################################
def WebTrack(dir, track):
    title=track[0] + " - " + track[1]
    url = track[3]
    if not track[4]:
        title = title + " (Not Streamable)"
        url = "garbage"
    
    dir.Append(WebVideoItem(url, title=title, thumb=track[2]))
    
##########################################################################
def IsYouTube(thumb):
    return (thumb.find('youtube.com') > -1) or (thumb.find('ytimg.com') > -1)

##########################################################################
# Some are Last.FM whereas some are from YouTube. I haven't seen other places
def Videos(sender, artist, page=1):
    dir = MediaContainer(mediaType='video', title2=sender.itemTitle) 
    videos = LastFm.ArtistVideos(artist[0], page)
    for video in videos[0]:
        
        isYouTube = IsYouTube(video[1])
        if(isYouTube):
           videoUrl = YouTubeVideoUrl(video)
           dir.Append(VideoItem(videoUrl, title=video[0], thumb=video[1]))
        else:
           videoUrl = LastFmVideoUrl(video, artist)
           dir.Append(VideoItem(videoUrl, title=video[0], thumb=video[1]))
    if videos[1]:
        dir.Append(Function(DirectoryItem(Videos, title="More ..."), artist=artist, page=page+1))
    return dir
    
############################################
def LastFmVideoUrl(sender, video, artist):
    videoId = video[2].split('/')[-1]
    playList = HTTP.Request(VIDEO_PLAY_LIST % (videoId, String.Quote(artist[0], True)))
    start = playList.index('<location>') + 10
    stop = playList.index('</location>')
    videoUrl = playList[start:stop]
    return videoUrl
    
############################################
# A little borrowing from the YouTube plugin here. Thanks.
def YouTubeVideoUrl(video):
    videoId = video[2].split('/')[-1].replace('+1-','')
    ytPage = HTTP.Request(YOU_TUBE_PAGE % videoId)
    t = re.findall('"t": "([^"]+)"', ytPage)[0]
    v = re.findall("'VIDEO_ID': '([^']+)'", ytPage)[0] #
    hd = re.findall("'IS_HD_AVAILABLE': ([^,]+),", ytPage)[0] #
    
    fmt = "18"
    if hd == "true":
      fmt = "22"
      
    videoUrl = "http://www.youtube.com/get_video?video_id=%s&t=%s&fmt=%s" % (v, t, fmt)
    return videoUrl

