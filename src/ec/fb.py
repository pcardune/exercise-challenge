import urllib

from tornado.options import define, options
from tornado import httpclient, escape

from ec.log import logger
from ec import cache

define("fb_endpoint", default="graph.facebook.com", help="Facebook API Endpoint")
define("fb_app_id", default='125917107430749')
define("fb_app_secret", default='2074ea14556a918a1046993130301328')
define("fb_api_key", default='6404a70cad8e247dd9a3f89c4aca56f8')


def get_url(path, args=None, secure=False):
    args = args or {}
    if secure or 'access_token' in args:
        endpoint = "https://"+options.fb_endpoint
    else:
        endpoint = "http://"+options.fb_endpoint
    return endpoint+path+'?'+urllib.urlencode(args)


def get_authorization_url(redirect_url, scope=[]):
    return get_url('/oauth/authorize',
                   args={'client_id':options.fb_app_id,
                         'scope':','.join(scope),
                         'redirect_uri':redirect_url},
                   secure=True)


def get_access_token(code, redirect_url, callback):
    url = get_url('/oauth/access_token',
                  args={'client_id': options.fb_app_id,
                        'redirect_uri': redirect_url,
                        'client_secret': options.fb_app_secret,
                        'code':code})

    httpclient.AsyncHTTPClient().fetch(url, callback=callback)

def get_user_cachekey(fbid, viewer):
    return "user:%s:%s" % (fbid, viewer.fbid)

def get_user(fbid, viewer, callback):
    """Get a user from the cache.

    This will fetch from facebook if they are not in the cache.
    """
    user = cache.get(get_user_cachekey(fbid, viewer))
    if user:
        callback(user)
    else:
        def wrapper(user):
            cache.set(get_user_cachekey(fbid, viewer), user)
            callback(user)
        fbget_user(fbid, viewer, wrapper)

def fbget_user(fbid, viewer, callback):
    """Return the given user data in the context of the viewer.

    This will always make an api call to facebook.  You probably want to use
    get_user
    """
    url = get_url('/%s' % fbid,
                  args={'access_token':viewer.fb_access_token})
    logger.info("fetching url %s", url)
    def wrapper(response):
        if not response.error:
            callback(escape.json_decode(response.body))
        else:
            callback(None)
    httpclient.AsyncHTTPClient().fetch(url, callback=wrapper)

def fbget_self(access_token, callback):
    """Return the user associated with the given access token."""
    url = get_url('/me',
                  args={'access_token':access_token})
    logger.info("fetching url %s", url)
    def wrapper(response):
        if not response.error:
            callback(escape.json_decode(response.body))
        else:
            callback(None)
    httpclient.AsyncHTTPClient().fetch(url, callback=wrapper)
