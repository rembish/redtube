from urllib2 import urlopen, Request, URLError
from datetime import datetime
from urllib import urlencode
from sys import version_info
from base64 import b64decode
from weakref import ref
from json import loads
from copy import copy
from math import pow

__version__ = '0.3.5'

class RedException(Exception):
    pass

class RedVideo(object):
    def __init__(self, client, kwargs):
        self.id = kwargs['video_id']
        self.title = kwargs['title']

        self.url = kwargs['url']
        self.thumbnail_url = kwargs['thumb']

        self.published = datetime.strptime(kwargs['publish_date'], '%Y-%m-%d %H:%M:%S') if kwargs['publish_date'] else None
        self.duration = int(sum(map(lambda x: x[1] * pow(60, x[0]), enumerate(map(int, kwargs['duration'].split(':')[::-1])))))

        self.tags = [entry if isinstance(entry, basestring) else entry['tag_name'] for entry in kwargs.get('tags', [])]
        self.stars = [entry if isinstance(entry, basestring) else entry['star_name'] for entry in kwargs.get('stars', [])]

        self.thumbnails = {}
        for entry in kwargs.get('thumbs', []):
            if entry['size'] not in self.thumbnails:
                self.thumbnails[entry['size']] = {
                    'dimensions': (entry['width'], entry['height']),
                    'thumbnails': [],
                }
            self.thumbnails[entry['size']]['thumbnails'].append(entry['src'])

        self._client = ref(client)
        self._active = None
        self._code = None

    def __repr__(self):
        return '<%s[%s] "%s">' % (self.__class__.__name__, self.id, self.title)

    @property
    def client(self):
        if self._client() is None:
            return RedClient()
        return self._client()

    @property
    def active(self):
        if self._active is None:
            self._active = bool(self.client._request('redtube.Videos.isVideoActive', video_id=self.id)['active']['is_active'])
        return self._active

    @property
    def embed(self):
        if not self._code:
            self._code = b64decode(self.client._request('redtube.Videos.getVideoEmbedCode', video_id=self.id)['embed']['code'])
        return self._code

    @property
    def player_url(self):
        return 'http://embed.redtube.com/player/?id=%s' % self.id

class RedCollection(list):
    def __init__(self, client, data):
        self._client = ref(client)
        json = self.client._request('redtube.Videos.searchVideos', **data)

        super(RedCollection, self).__init__(
            RedVideo(client, entry['video']) for entry in json['videos']
        )

        self.query = data
        self.total = json['count']
        self.page = self.query.get('page', 1)

    @property
    def client(self):
        if self._client() is None:
            return RedClient()
        return self._client()

    def next(self):
        if len(self) * (self.start + 1) > self.total:
            return None

        data = copy(self.query)
        data['page'] = data.get('page', 1) + 1
        return self.__class__(self.client, data)

class RedClient(object):
    server = 'http://api.redtube.com/'
    thumbnail_sizes = ['all', 'small', 'medium', 'medium1', 'medium2', 'big']

    def __init__(self):
        self._categories = []
        self._tags = []
        self._stars = []

    def _request(self, data, **kwargs):
        kwargs.update({'output': 'json', 'data': data})
        url = '%s?%s' % (self.server, urlencode(kwargs))
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

        data = {'page': int(page)}
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

        return RedCollection(self, data)

    def by_id(self, id, thumbnail_size=None):
        if thumbnail_size not in self.thumbnail_sizes:
            thumbnail_size = None

        data = {'video_id': id}
        if thumbnail_size:
            data['thumbsize'] = thumbnail_size

        try:
            return RedVideo(self, self._request('redtube.Videos.getVideoById', **data)['video'])
        except KeyError:
            return None

    def __getitem__(self, id):
        return self.by_id(id)

    @property
    def categories(self):
        if not self._categories:
            self._categories = [
                entry['category'] for entry in self._request('redtube.Categories.getCategoriesList')['categories']
            ]
        return self._categories

    @property
    def tags(self):
        if not self._tags:
            self._tags = [
                entry['tag']['tag_name'] for entry in self._request('redtube.Tags.getTagList')['tags']
            ]
        return self._tags

    @property
    def stars(self):
        if not self._stars:
            self._stars = [
                entry['star']['star_name'] for entry in self._request('redtube.Stars.getStarList')['stars']
            ]
        return self._stars
