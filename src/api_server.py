import endpoints
from apis.UserApi import UserApi
from apis.MealApi import MealApi


API_SERVER = endpoints.api_server([UserApi, MealApi], restricted = False)