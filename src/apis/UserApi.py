#required for endpoints to work
from google.appengine.ext import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

"""
Application Specific Error Messages

-1 => Invalid username, email or password
-2 => User is already registered
"""

errorMessages = {
	-1: "Invalid username, email or password",
	-2: "User is already registered"
}


"""
Request ProtoRPC messages
"""
class SignUpUserRequestMessage(messages.Message):
    firstName = messages.StringField(1, required=True)
    lastName = messages.StringField(2, required=True)
    email = messages.StringField(3, required=True)
    password = messages.StringField(4, required=True)


"""
Response ProtoRPC messages
"""
class SignUpUserResponseMessage(messages.Message):
    authToken = messages.StringField(1, required=False)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)


@endpoints.api(name='userService', version='v1', description='API for working with a User', hostname='cafbuddy.appspot.com')  
class UserApi(remote.Service):

	"""
    Creates user with encrypted password, returning auth token for validation
    """
    @endpoints.method(SignUpUserRequestMessage, SignUpUserResponseMessage, name='User.signupUser', path='signupUser', http_method='POST')
    def signupUser(self, request):
        
        #makes sure required fields aren't blank
        if (request.firstName == "") or (request.lastName == "") or (request.password == "") or (request.email == ""):
            return SignUpUserResponseMessage(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #calls backend function, returns token of user
        # userData = user.User.signUpUser(request.userName, request.email, request.password)
        
        # if not userData[0]:
            # return authTokenMessage(errorMessage = userData[1], errorNumber = userData[2])
        
        #get auth token message
        # return authTokenMessage(authToken = userData[1], errorNumber = 200)



























