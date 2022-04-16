class Cache(object):
    def __init__(self):
        self.cache = dict()

    def get_or_load(self, key, loadFn):
        value = self.cache.get(key)
        if value == None:
            value = loadFn(key)
            self.cache[key] = value
        return value

    def purge(self):
        self.cache = dict()
