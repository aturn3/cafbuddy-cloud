import endpoints
from apis.UserApi import UserApi

API_SERVER = endpoints.api_server([UserApi], restricted=False)