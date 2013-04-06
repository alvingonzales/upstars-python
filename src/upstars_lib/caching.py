
try:
    from google.appengine.api.memcache import Client as CacheClient
except ImportError:

    _CacheClient = None

    class CacheClientClass:
        def __init__(self):
            self.objects = {}

        def get(self, id):
            if id in self.objects:
                return self.objects[id]
            else:
                return None

        def set(self, id, value):
            self.objects[id] = value

    def CacheClient():
        global _CacheClient
        if not _CacheClient:
            _CacheClient = CacheClientClass()

        return _CacheClient
