from google.appengine.ext import endpoints

from APIs import User


application = endpoints.api_server([User.UserApi, restricted=False)