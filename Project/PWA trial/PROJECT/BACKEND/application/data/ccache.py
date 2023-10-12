from flask import current_app as app
from flask_caching import Cache
cache=None
def create_cache():
    app.config['CACHE_TYPE']='RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    cache=Cache(app)
    return cache
cache=create_cache()