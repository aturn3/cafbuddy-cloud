#required for endpoints to work
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from classes.User import User

"""
Application Specific Error Messages

-1 => Invalid email or password
-2 => User is already registered
-3 => Required fields are missing
-4 => Email address must be a valid St. Olaf College email
-5 => User was unable to be validated as logged in
"""

errorMessages = {
	-1: "Invalid email or password.",
	-2: "You are already registered.",
	-3: "Required fields are missing.",
	-4: "Email address must be a valid St. Olaf College email.",
	-5: "You are not logged in."
}


"""
Request ProtoRPC messages
"""
class SignUpUserRequestMessage(messages.Message):
	firstName = messages.StringField(1, required = True)
	lastName = messages.StringField(2, required = True)
	emailAddress = messages.StringField(3, required = True)
	password = messages.StringField(4, required = True)

class LogInUserRequestMessage(messages.Message):
	emailAddress = messages.StringField(1, required = True)
	password = messages.StringField(2, required = True)

class LogOutUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

class ValidateUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

"""
Response ProtoRPC messages
"""	
class SignUpUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)
	authToken = messages.StringField(3, required = False)

class LogInUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)
	authToken = messages.StringField(3, required = False)

class LogOutUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class ValidateUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)


@endpoints.api(name='userService', version='v1.011', description='API for working with a User', hostname='cafbuddy.appspot.com')  
class UserApi(remote.Service):

	"""
	Creates user with encrypted password, returning auth token for validation
	"""
	@endpoints.method(SignUpUserRequestMessage, SignUpUserResponseMessage, name='signupUser', path='signupUser', http_method='POST')
	def signupUser(self, request):        
		if (request.firstName == "") or (request.lastName == "") or (request.password == "") or (request.emailAddress == ""):
			return SignUpUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)

		#make sure its a st olaf email address
		if "@stolaf.edu" not in request.emailAddress:
			return SignUpUserResponseMessage(errorMessage = errorMessages[-4], errorNumber = -4)
		
		#calls backend function, returns token of user if success or error number if error
		success, authTokOrErrorNum = User.signUp(request.firstName, request.lastName, request.emailAddress, request.password)
		if not success:
			return SignUpUserResponseMessage(errorMessage = errorMessages[authTokOrErrorNum], errorNumber = authTokOrErrorNum)        
		return SignUpUserResponseMessage(authToken = authTokOrErrorNum, errorNumber = 200)

	"""
	login method using password and email/username (store in userName field), returns auth token
	"""
	@endpoints.method(LogInUserRequestMessage, LogInUserResponseMessage, name='loginUser', path='loginUser', http_method='POST')
	def loginUser(self, request):
		if (request.password == "") or (request.emailAddress == ""):
			return LogInUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		#calls user backend function, returns token of user
		success, authTokOrErrorNum = User.logIn(request.emailAddress, request.password)
		
		if not success:
			return LogInUserResponseMessage(errorMessage = errorMessages[authTokOrErrorNum], errorNumber = authTokOrErrorNum)
		return LogInUserResponseMessage(authToken = authTokOrErrorNum, errorNumber = 200)
		
		
	"""
	logout method, simply deletes authtoken from backend
	"""
	@endpoints.method(LogOutUserRequestMessage, LogOutUserResponseMessage, name='logoutUser', path='logoutUser', http_method='POST')    
	def logoutUser(self,request):
		if (request.emailAddress == "") or (request.authToken == ""):
			return LogOutUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		success = User.logOut(request.emailAddress, request.authToken)
		if(success):
			return LogOutUserResponseMessage(errorNumber = 200)
		else:
			return LogOutUserResponseMessage(errorNumber = 404)
		
		
	"""
	validate the user
	Can return: -3, -5
	"""
	@endpoints.method(ValidateUserRequestMessage, ValidateUserResponseMessage, name='validateUser', path='validateUser', http_method='POST')
	def validateUser(self, request):
		if (request.emailAddress == "") or (request.authToken == ""):
			return ValidateUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		#validates user
		userKey = User.validateLogIn(request.emailAddress, request.authToken)
		if not userKey:
			return ValidateUserResponseMessage(errorMessage = errorMessages[-5], errorNumber = -5)
		return ValidateUserResponseMessage(errorNumber = 200);

