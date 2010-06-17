import urllib

from tornado.options import define, options
from tornado import httpclient, escape

from ec.log import logger
from ec import cache
import ec.users

define("fb_endpoint", default="graph.facebook.com", help="Facebook API Endpoint")
define("fb_app_id", default='125917107430749')
define("fb_app_secret", default='2074ea14556a918a1046993130301328')
define("fb_api_key", default='6404a70cad8e247dd9a3f89c4aca56f8')


def get_url(path, args=None, secure=False):
    """Get a url to facebook with the proper query parameters."""
    args = args or {}
    if secure or 'access_token' in args:
        endpoint = "https://"+options.fb_endpoint
    else:
        endpoint = "http://"+options.fb_endpoint
    return endpoint+path+'?'+urllib.urlencode(args)


def get_authorization_url(redirect_url, scope=[]):
    """Get the authorization url to redirect the user to."""
    return get_url('/oauth/authorize',
                   args={'client_id':options.fb_app_id,
                         'scope':','.join(scope),
                         'redirect_uri':redirect_url},
                   secure=True)


def get_access_token(code, redirect_url, callback):
    """Get the access token using the code provided to the redirect url."""
    url = get_url('/oauth/access_token',
                  args={'client_id': options.fb_app_id,
                        'redirect_uri': redirect_url,
                        'client_secret': options.fb_app_secret,
                        'code':code})

    httpclient.AsyncHTTPClient().fetch(url, callback=callback)

@cache.key
def get_user_cachekey(fbid, viewer):
    return "user:%s:%s" % (fbid, viewer.fbid)

@cache.key
def get_user_friends_cachekey(fbid, viewer):
    return "friends:%s:%s" % (fbid, viewer.fbid)

@cache.key
def dbget_user_friends_on_here_cachekey(fbid, viewer):
    return "friends-local:%s:%s" % (fbid, viewer.fbid)

def _cache_get(key, callback, getter_func, *args):
    result = cache.get(key)
    if result:
        callback(result)
    else:
        def wrapper(result, error=None):
            if not error:
                cache.set(key, result)
            callback(result, error=error)
        getter_func(*(args+(wrapper,)))


def get_user(fbid, viewer, callback):
    """Get a user from the cache.

    This will fetch from facebook if they are not in the cache.
    """
    _cache_get(get_user_cachekey(fbid, viewer),
               callback,
               fbget_user,
               fbid, viewer)

def get_user_friends(fbid, viewer, callback):
    _cache_get(get_user_friends_cachekey(fbid, viewer),
               callback,
               fbget_user_friends,
               fbid, viewer)

def get_user_friends_on_here(fbid, viewer, callback):
    _cache_get(dbget_user_friends_on_here_cachekey(fbid, viewer),
               callback,
               dbget_user_friends_on_here,
               fbid, viewer)

def _json_callback_wrapper(callback):
    def wrapper(response):
        if not response.error:
            callback(escape.json_decode(response.body))
        else:
            logger.warn("Error: %r", response.error)
            callback(None, error=response)
    return wrapper

def _get_json(path, callback, viewer=None, args=None):
    args = args or {}
    if viewer and viewer.fb_access_token:
        args['access_token'] = viewer.fb_access_token
    url = get_url(path,args=args)
    logger.info("fetching url %s", url)
    httpclient.AsyncHTTPClient().fetch(
        url, callback=_json_callback_wrapper(callback))

def fbget_user(fbid, viewer, callback):
    """Return the given user data in the context of the viewer.

    This will always make an api call to facebook.  You probably want to use
    get_user
    """
    _get_json('/%s' % fbid, callback, viewer=viewer)


def fbget_user_friends(fbid, viewer, callback):
    """Returns the friends for the given user in the context of the viewer."""
    _get_json('/%s/friends' % fbid, callback, viewer=viewer)


def fbget_self(access_token, callback):
    """Return the user associated with the given access token."""
    url = get_url('/me',
                  args={'access_token':access_token})
    logger.info("fetching url %s", url)
    def wrapper(response):
        if not response.error:
            callback(escape.json_decode(response.body))
        else:
            callback(None, error=response.body)
    httpclient.AsyncHTTPClient().fetch(url, callback=wrapper)

def dbget_user_friends_on_here(fbid, viewer, callback):
    def _on_get_user_friends(friends, error=None):
        if error:
            callback(None, error)
        else:
            friend_by_fbid = dict((long(f['id']),f) for f in friends['data'])
            local_friends = ec.users.get_users_with_fbids(friend_by_fbid.keys())
            for friend in local_friends:
                friend['fbuser'] = friend_by_fbid[friend.fbid]
            callback(local_friends)
    get_user_friends(fbid, viewer, _on_get_user_friends)
