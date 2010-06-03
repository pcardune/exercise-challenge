import urllib

from tornado.options import define, options
from tornado import httpclient

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


def get_authorization_url(redirect_url):
    return get_url('/oauth/authorize',
                   args={'client_id':options.fb_app_id,
                         'redirect_uri':redirect_url},
                   secure=True)

def get_access_token(code, redirect_url, callback):
    url = get_url('/oauth/access_token',
                  args={'client_id': options.fb_app_id,
                        'redirect_uri': redirect_url,
                        'client_secret': options.fb_app_secret,
                        'code':code})

    httpclient.AsyncHTTPClient().fetch(url, callback=callback)

def get_user(access_token, callback):
    url = get_url('/me',
                  args={'access_token':access_token})
    httpclient.AsyncHTTPClient().fetch(url, callback=callback)
