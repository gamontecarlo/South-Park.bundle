import random

NAME = 'South Park'
BASE_URL = 'http://www.southparkstudios.com'
GUIDE_URL = 'http://www.southparkstudios.com/full-episodes'
SEASON_JSON_URL = 'http://www.southparkstudios.com/feeds/full-episode/carousel/%s/dc400305-d548-4c30-8f05-0f27dc7e0d5c' # season
RANDOM_URL = 'http://www.southparkstudios.com/full-episodes/random'

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'

###################################################################################################
@handler('/video/southpark', NAME)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	oc.add(DirectoryObject(
		key = Callback(RandomEpisode),
		title = L('RANDOM_TITLE')
	))

	num_seasons = len(HTML.ElementFromURL(GUIDE_URL).xpath('//li/a[contains(@href, "full-episodes/season-")]'))

	for season in range(1, num_seasons+1):
		title = F("SEASON", str(season))
		oc.add(DirectoryObject(
			key = Callback(Episodes, title=title, season=str(season)),
			title = title
		))

	return oc

####################################################################################################
@route('/video/southpark/episodes')
def Episodes(title, season):

	oc = ObjectContainer(title2=title)

	for episode in JSON.ObjectFromURL(SEASON_JSON_URL % season)['season']['episode']:

		if episode['available'] != 'true':
			continue

		url = unicode(episode['url'])
		title = episode['title']
		summary = episode['description']
		originally_available_at = Datetime.ParseDate(episode['airdate'])
		index = episode['episodenumber'][-2:]
		thumb = episode['thumbnail'].split('?')[0]

		oc.add(EpisodeObject(
			url = url,
			show = NAME,
			title = title,
			summary = summary,
			originally_available_at = originally_available_at,
			season = int(season),
			index = int(index),
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="This season doesn't contain any episodes.")
	else:
		oc.objects.sort(key = lambda obj: obj.index)
		return oc

###################################################################################################
#@indirect
@route('/video/southpark/episodes/random')
def RandomEpisode():
	num_seasons = len(HTML.ElementFromURL(GUIDE_URL).xpath('//li/a[contains(@href, "full-episodes/season-")]'))
	season = random.randint(1,int(num_seasons))
	
	episodeList = list()
	
	eps = JSON.ObjectFromURL(SEASON_JSON_URL % season)['season']['episode']
	
	for index, episode in enumerate(eps):
		if episode['available'] != 'true':
			continue
		episodeList.append(index)
		
	episode = eps[random.choice(episodeList)]
	
	return IndirectResponse(VideoClipObject,
		url = unicode(episode['url']),
		key = unicode(episode['url']),
	)
