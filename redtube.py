from urllib2 import urlopen, Request, URLError
from dateutil.parser import parse
from base64 import b64decode
from simplejson import loads
from sys import version_info
from furl import furl
from math import pow

__version__ = '0.2'

class RedException(Exception):
    pass

class RedVideo(object):
    def __init__(self, client, **kwargs):
        self.id = kwargs['video_id']
        self.title = kwargs['title']

        self.url = kwargs['url']
        self.thumbnail_url = kwargs['thumb']

        self.published = parse(kwargs['publish_date']) if kwargs['publish_date'] else None
        self.duration = int(sum(map(lambda x: x[1] * pow(60, x[0]), enumerate(map(int, kwargs['duration'].split(':')[::-1])))))

        self.tags = [entry if isinstance(entry, basestring) else entry['tag_name'] for entry in kwargs.get('tags', {})]
        self.stars = [entry['star_name'] for entry in kwargs.get('stars', {})]

        self.thumbnails = {}
        for entry in kwargs.get('thumbs', []):
            if entry['size'] not in self.thumbnails:
                self.thumbnails[entry['size']] = {
                    'dimensions': (entry['width'], entry['height']),
                    'thumbnails': [],
                }
            self.thumbnails[entry['size']]['thumbnails'].append(entry['src'])

        self._client = client
        self._active = None
        self._code = None

    def __repr__(self):
        return '<%s[%s] "%s">' % (self.__class__.__name__, self.id, self.title)

    @property
    def active(self):
        if self._active is None:
            self._active = bool(self._client._request('redtube.Videos.isVideoActive', video_id=self.id)['active']['is_active'])
        return self._active

    @property
    def embed(self):
        if not self._code:
            self._code = b64decode(self._client._request('redtube.Videos.getVideoEmbedCode', video_id=self.id)['embed']['code'])
        return self._code

    @property
    def player_url(self):
        return 'http://embed.redtube.com/player/?id=%s' % self.id

class RedClient(object):
    server = 'http://api.redtube.com/'
    thumbnail_sizes = ['all', 'small', 'medium', 'medium1', 'medium2', 'big']

    def _request(self, data, **kwargs):
        url = furl(self.server).set({'output': 'json', 'data': data}).add(kwargs)
        request = Request(str(url), headers={
            'User-Agent': 'RedTubeClient/%s (Python/%s)' % (
                __version__, '.'.join(map(str, version_info[:-2]))
            )
        })

        try:
            response = urlopen(request).read()
            return loads(response)
        except URLError as e:
            raise RedException(str(e))

    def search(self, query=None, category=None, tags=[], stars=[], thumbnail_size=None, page=1):
        if thumbnail_size not in self.thumbnail_sizes:
            thumbnail_size = None
        if page < 1:
            page = 1

        data = {}
        if query:
            data['search'] = query
        if category:
            data['category'] = category
        if tags:
            data['tags'] = tags
        if stars:
            data['stars'] = stars
        if thumbnail_size:
            data['thumbsize'] = thumbnail_size

        return [
            RedVideo(self, **entry['video']) for entry in self._request('redtube.Videos.searchVideos', **data)['videos']
        ]

    def get_by_id(self, id, thumbnail_size=None):
        if thumbnail_size not in self.thumbnail_sizes:
            thumbnail_size = None

        data = {'video_id': id}
        if thumbnail_size:
            data['thumbsize'] = thumbnail_size

        return RedVideo(self, **self._request('redtube.Videos.getVideoById', **data)['video'])

    def getCategories(self):
        return [
            entry['category'] for entry in self._request('redtube.Categories.getCategoriesList')['categories']
        ]

    def getTags(self):
        return [
            entry['tag']['tag_name'] for entry in self._request('redtube.Tags.getTagList')['tags']
        ]

    def getStars(self):
        return [
            entry['star']['star_name'] for entry in self._request('redtube.Stars.getStarList')['stars']
        ]
