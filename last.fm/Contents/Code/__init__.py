import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from LastFm import *

MUSIC_PREFIX      = "/music/lastfm"
VIDEO_PREFIX      = "/video/lastfm"
CACHE_INTERVAL    = 1800
REFRESH_RATE = 5

# Two video types - Last.FM and YouTube
VIDEO_PLAY_LIST = "http://ext.last.fm/1.0/video/getplaylist.php?&vid=%s&artist=%s"
YOU_TUBE_PAGE = "http://www.youtube.com/watch?v=%s" 

# Context menu map keys
ITEM = "item"

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
  
def ValidatePrefs():
    LastFm.Authenticate()
    
##################################
def MainMenu():
    dir = MediaContainer(mediaType='video', autoRefresh=REFRESH_RATE ) 
    if LastFm.IsAuthenticated():
        user = LastFm.CurrentUser()
        dir.Append(Function(DirectoryItem(Radios, "Radios"), user = user))
        dir.Append(Function(DirectoryItem(Library, "Library"), user = user))
        dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks"), user = user))
        dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks"), user = user))
        dir.Append(Function(DirectoryItem(RecommendedArtists, "Recommended Artists")))
        
        dir.Append(Function(DirectoryItem(UserTopArtists, "Top Artists"), user = user))
        dir.Append(Function(DirectoryItem(UserTopAlbums, "Top Albums"), user = user))
        dir.Append(Function(DirectoryItem(UserTopTracks, "Top Tracks"), user = user))
    
    dir.Append(Function(DirectoryItem(TagTopTags, "Top Tags")))
    if LastFm.IsAuthenticated():
        user = LastFm.CurrentUser()
        dir.Append(Function(DirectoryItem(Friends, "Friends"), user = user))
        dir.Append(Function(DirectoryItem(Neighbours, "Neighbours"), user = user))
    
    dir.Append(Function(InputDirectoryItem(SearchAlbumsResults, title="Search Albums ...", prompt="Search Albums", thumb=S('Search'))))
    dir.Append(Function(InputDirectoryItem(SearchArtistsResults, title="Search Artists ...", prompt="Search Artists", thumb=S('Search'))))
    dir.Append(Function(InputDirectoryItem(SearchTagsResults, title="Search Tags ...", prompt="Search Tags", thumb=S('Search'))))
    dir.Append(PrefsItem(L("Preferences ..."), thumb=R('icon-prefs.png')))
    return dir
    

########################################################
def Radios(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    name = None
    if user.isCurrentUser:
        name = "your"
    else:
        name = user.name+"'s"
        
    dir.Append(Function(VideoItem(PlayRadio, "Play "+name+" Library", thumb=R("icon-default.png")), url=user.libraryRadioUrl))
    # Loved tracks radio was causing an error in the browser also
    #dir.Append(Function(VideoItem(PlayRadio, "Play "+name+" Loved Tracks", thumb=R("icon-default.png")), url=user.lovedRadioUrl))
    dir.Append(Function(VideoItem(PlayRadio, "Play "+name+" Recommendations", thumb=R("icon-default.png")), url=user.recommendedRadioUrl))
    dir.Append(Function(VideoItem(PlayRadio, "Play "+name+" Neighbourhood", thumb=R("icon-default.png")), url=user.neighoursRadioUrl))
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
   
    dir.Append(Function(DirectoryItem(Radios, "Radios"), user = user))
    dir.Append(Function(DirectoryItem(Library, "Library"), user = user))
    dir.Append(Function(DirectoryItem(RecentTracks, "Recent Tracks"), user = user))
    dir.Append(Function(DirectoryItem(LovedTracks, "Loved Tracks"), user = user))
    
    dir.Append(Function(DirectoryItem(UserTopArtists, "Top Artists"), user = user))
    dir.Append(Function(DirectoryItem(UserTopAlbums, "Top Albums"), user = user))
    dir.Append(Function(DirectoryItem(UserTopTracks, "Top Tracks"), user = user))
    dir.Append(Function(DirectoryItem(UserTopTags, "Top Tags"), user = user))
    dir.Append(Function(DirectoryItem(Friends, "Friends"), user = user))
    dir.Append(Function(DirectoryItem(Neighbours, "Neighbours"), user = user))
    return dir


########################################################
def Library(sender, user):
    dir = MediaContainer(title2=sender.itemTitle)
    dir.Append(Function(DirectoryItem(LibraryAlbums, "Albums"), user = user))
    dir.Append(Function(DirectoryItem(LibraryArtists, "Artists"), user = user))
    dir.Append(Function(DirectoryItem(LibraryTracks, "Tracks"), user = user))
    title = None
    if user.isCurrentUser:
        title = "Play your Library"
    else:
        title = "Play "+user.name+"'s Library"
    dir.Append(Function(VideoItem(PlayRadio, title, thumb=R("icon-default.png")), url=user.libraryRadioUrl))
    return dir

########################################################
def LibraryAlbums(sender, user ): 
    return AppendAlbums(sender, user.libraryAlbums)

########################################################
def LibraryArtists(sender, user):
    return AppendArtists(sender, user.libraryArtists)

########################################################
def LibraryTracks(sender, user, page=1):    
    tracksTuple = user.getLibraryTracks(page)
    dir = AppendTracks(sender, tracksTuple[0])
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LibraryTracks, "More ..."), user = user, page = page+1))
    return dir

########################################################
def RecommendedArtists(sender):    
    return AppendArtists(sender, LastFm.RecommendedArtists())
    
##########################################################################
def LovedTracks(sender, user, page=1):
    tracksTuple = user.getLovedTracks(page)
    dir = AppendTracks(sender, tracksTuple[0])
    if tracksTuple[1]:
        dir.Append(Function(DirectoryItem(LovedTracks, "More ..."), user = user, page = page+1))
    return dir

##########################################################################
def RecentTracks(sender, user):
    return AppendTracks(sender, user.recentTracks)

#######################################################################
def Category(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(TagTopArtists, "Top Artists"), tag = tag))
    dir.Append(Function(DirectoryItem(TagTopAlbums, "Top Albums"), tag = tag))
    dir.Append(Function(DirectoryItem(TagTopTracks, "Top Tracks"), tag = tag))
    dir.Append(Function(DirectoryItem(ArtistChart, "Weekly Artist Chart"), tag=tag))
    dir.Append(Function(DirectoryItem(SimilarTags, "Similar Tags"), tag=tag))
    radioTitle = "Play " + tag.name.capitalize() + " Radio"
    dir.Append(Function(VideoItem(PlayRadio, radioTitle, thumb=R("icon-default.png")), url=tag.radioUrl))
    return dir


#######################################################################
# Paid subscription account will alter this. A lot.
#######################################################################
def PlayRadio(sender, url):
    return Redirect(WebVideoItem(url))

#######################################################################
def ArtistChart(sender, tag):
    dir = MediaContainer(viewGroup='Details',title2=sender.itemTitle) 
    @progressive_load(dir)
    def ArtistChartPageLoader(dir):
        for artist in tag.artistChart:
            subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
            dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary), artist = artist))
    return ArtistChartPageLoader

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
    return AppendArtists(sender, artists)

##########################################################################
def TopAlbums(sender, albums):
    return AppendAlbums(sender, albums)

##########################################################################
def TopTracks(sender, tracks):
    return AppendTracks(sender, tracks)

#######################################################################
def TopTags(sender, tags):
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle) 
    @progressive_load(dir)
    def TopTagsPageLoader(dir):
        for tag in tags:
            subtitle = "Tag Count: " + tag.tagCount
            dir.Append(Function(DirectoryItem(Category, title=tag.name.capitalize(), subtitle=subtitle), tag = tag))
    return TopTagsPageLoader

############################################################################
def ArtistDirectory(sender, artist):
    dir = MediaContainer(title2=sender.itemTitle) 
    dir.Append(Function(DirectoryItem(ArtistVideos, title="Videos", thumb=artist.image, summary=artist.summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistTracks, title="Tracks", thumb=artist.image, summary=artist.summary), artist = artist))
    dir.Append(Function(DirectoryItem(ArtistAlbums, title="Albums", thumb=artist.image, summary=artist.summary), artist = artist))
    if artist.streamable:
        title = "Play "+artist.name+" Radio"
        dir.Append(Function(VideoItem(PlayRadio, title, thumb=artist.image, summary=artist.summary), url=artist.radioUrl))
    dir.Append(Function(DirectoryItem(SimilarArtists, title="Similar Artists", thumb=artist.image, summary=artist.summary), artist = artist))
    return dir

############################################################################
def AlbumDirectory(sender, album):
    return AppendTracks(sender, album.trackList)

########################################################
def AppendArtists(sender, artists):
    menu = ContextMenu(includeStandardItems=False)
    menu.Append(Function(DirectoryItem(AddToLibrary, title="Add to Library")))
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu)
    @progressive_load(dir)
    def ArtistsPageLoader(dir):
        for artist in artists:
            subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
            dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary, contextKey=artist.name, contextArgs={ITEM:artist}), artist = artist))
    return ArtistsPageLoader

########################################################
def AppendAlbums(sender, albums):
    menu = ContextMenu(includeStandardItems=False)
    menu.Append(Function(DirectoryItem(AddToLibrary, title="Add to Library")))
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu) 
    @progressive_load(dir)
    def AlbumsPageLoader(dir):
        for album in albums:
            title = album.name + " - " + album.artist
            subtitle = str(album.plays) +" plays ("+ str(album.listeners) + " listeners)"
            dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary, contextKey=title, contextArgs={ITEM:album}), album = album))
    return AlbumsPageLoader

############################################################################
def AppendTracks(sender, tracks):
    menu = ContextMenu(includeStandardItems=False)
    menu.Append(Function(DirectoryItem(AddToLibrary, title="Add to Library")))
    menu.Append(Function(DirectoryItem(LoveTrack, title="Love Track")))
    menu.Append(Function(DirectoryItem(BanTrack, title="Ban Track")))
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu) 
    @progressive_load(dir)
    def TracksPageLoader(dir):
        for track in tracks:
            AppendTrack(dir, track)
    return TracksPageLoader

############################################################################
def AppendTrack(dir, track):
    title=track.name + " - " + track.artist
    url = track.url
    subtitle = str(track.plays) +" plays ("+ str(track.listeners) + " listeners)"
    if not track.streamable:
        subtitle = subtitle + "\nNot Streamable"
        url = "garbage"
    
    dir.Append(WebVideoItem(url, title=title, subtitle=subtitle, thumb=track.image, summary=track.summary, contextKey=title, contextArgs={ITEM:track}))

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
    return AppendAlbums(sender, artist.albums)

#######################################################
def ArtistTracks(sender, artist):
    return AppendTracks(sender, artist.tracks)

##########################################################################
def SimilarTags(sender, tag):
    dir = MediaContainer(title2=sender.itemTitle) 
    
    @progressive_load(dir)
    def SimilarTagsPageLoader(dir):
        for similarTag in tag.similarTags:
            dir.Append(Function(DirectoryItem(Category, title=similarTag.name.capitalize()), tag = similarTag))
    return SimilarTagsPageLoader

#######################################################
def SimilarArtists(sender, artist):
    return AppendArtists(sender, artist.similarArtists)

#######################################################################
def SearchTagsResults(sender, query, page=1):
  dir = MediaContainer(title2=sender.itemTitle)
  results = LastFm.SearchTags(query, page)
  @progressive_load(dir)
  def SearchTagsResultsPageLoader(dir):
      for tag in results[0]:
        dir.Append(Function(DirectoryItem(Category, title=tag.name.capitalize()), tag = tag))
      if results[1]:
          dir.Append(Function(DirectoryItem(SearchTagsResults, "More ..."), query = query, page = page+1))
  return SearchTagsResultsPageLoader
  
#######################################################################
def SearchArtistsResults(sender, query, page=1):
    
    results = LastFm.SearchArtists(query, page)
    # This is the same as AppendArtists but with pagination
    menu = ContextMenu(includeStandardItems=False)
    menu.Append(Function(DirectoryItem(AddToLibrary, title="Add to Library")))
    dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu)
    @progressive_load(dir)
    def SearchArtistsPageLoader(dir):
        for artist in results[0]:
            subtitle = str(artist.plays) +" plays ("+ str(artist.listeners) + " listeners)"
            dir.Append(Function(DirectoryItem(ArtistDirectory, title=artist.name, subtitle=subtitle, thumb=artist.image, summary=artist.summary, contextKey=artist.name, contextArgs={ITEM:artist}), artist = artist))
        if results[1]:
            dir.Append(Function(DirectoryItem(SearchArtistsResults, "More ..."), query = query, page = page+1))
    return SearchArtistsPageLoader
  
#######################################################################
def SearchAlbumsResults(sender, query, page=1): 
  results = LastFm.SearchAlbums(query, page)
  # This is the same as AppendAlbum but with pagination
  menu = ContextMenu(includeStandardItems=False)
  menu.Append(Function(DirectoryItem(AddToLibrary, title="Add to Library")))
  dir = MediaContainer(viewGroup='Details', title2=sender.itemTitle, contextMenu=menu) 
  @progressive_load(dir)
  def SearchAlbumsPageLoader(dir):
        for album in results[0]:
            title = album.name + " - " + album.artist
            subtitle = str(album.plays) +" plays ("+ str(album.listeners) + " listeners)"
            dir.Append(Function(DirectoryItem(AlbumDirectory, title=title, subtitle=subtitle, thumb=album.image, summary=album.summary, contextKey=title, contextArgs={ITEM:album}), album = album))
        if results[1]:
            dir.Append(Function(DirectoryItem(SearchAlbumsResults, "More ..."), query = query, page = page+1))
  return SearchAlbumsPageLoader
  
##########################################################################
def AddToLibrary(sender, key, **kwargs):
    libraryItem = kwargs[ITEM]
    libraryItem.addToLibrary()
    
##########################################################################
def LoveTrack(sender, key, **kwargs):
    track = kwargs[ITEM]
    track.love()
    
##########################################################################
def BanTrack(sender, key, **kwargs):
    track = kwargs[ITEM]
    track.ban()
    
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

