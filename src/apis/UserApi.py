import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from classes.User import User
from classes.Ratings import Ratings
from classes.Compliment import Compliment


"""
Application Specific Error Numbers

-1 => Invalid email or password
-2 => User is already registered
-3 => Required fields are missing
-4 => Email address must be a valid St. Olaf College email
-100 => User was unable to be validated as logged in
"""

#The error messages that will be returned to their client and displayed to the user.
errorMessages = {
	-1: "Invalid email or password.",
	-2: "You are already registered.",
	-3: "Required fields are missing.",
	-4: "Email address must be a valid St. Olaf College email.",
	-100: "You are not logged in."
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
	password = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

class LogOutUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

class ValidateUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

class SendNewEmailVerificationRequestMessage(messages.Message):
	emailAddress = messages.StringField(1, required = True)

class IncrementPositiveRatingRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)
	userKeys = messages.StringField(3, repeated = True)

class IncrementNegativeRatingRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)
	userKeys = messages.StringField(3, repeated = True)

class AddReportToUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)
	reportType = messages.IntegerField(3, required = True)
	comments = messages.StringField(4, required = False)
	userKeys = messages.StringField(5, repeated = True)

class AddComplimentRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)
	comment = messages.StringField(3, required = True)
	userKeys = messages.StringField(4, repeated = True)
	mealKey = messages.StringField(5, required = True)

class GetComplimentsGivenToUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

class GetComplimentsGivenByUserRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)

"""
Response ProtoRPC message classes
"""
class ComplimentMessage(messages.Message):
	toUserKey = messages.StringField(1, required = True)
	giverUserKey = messages.StringField(2, required = True)
	mealKey = messages.StringField(3, required = True)
	comment = messages.StringField(4, required = True)

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
	firstName = messages.StringField(4, required = False)
	lastName = messages.StringField(5, required = False)

class LogOutUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class ValidateUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class SendNewEmailVerificationResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class IncrementPositiveRatingResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class IncrementNegativeRatingResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class AddReportToUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class AddComplimentResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)

class GetComplimentsGivenToUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)
	compliments = messages.MessageField(ComplimentMessage, 3, repeated = True)

class GetComplimentsGivenByUserResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)
	compliments = messages.MessageField(ComplimentMessage, 3, repeated = True)


@endpoints.api(name='userService', version='v1.0', description='API for working with a User', hostname='cafbuddy.appspot.com')  
class UserApi(remote.Service):

	"""
	Creates a new user with all of its attributes and logs in the user
	On Success: Returns the authToken necessary to validate the user and log out the user
	On Error: -2, -3, -4
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
		if (not success):
			return SignUpUserResponseMessage(errorMessage = errorMessages[authTokOrErrorNum], errorNumber = authTokOrErrorNum)        
		return SignUpUserResponseMessage(authToken = authTokOrErrorNum, errorNumber = 200)

	"""
	Logs in a user using their password and email
	On Success: Returns the authToken necessary to validate the user and log out the user
	On Error: -3
	"""
	@endpoints.method(LogInUserRequestMessage, LogInUserResponseMessage, name='loginUser', path='loginUser', http_method='POST')
	def loginUser(self, request):
		if (request.password == "") or (request.emailAddress == ""):
			return LogInUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		#calls user backend function, returns token of user
		success, authTokOrErrorNum, userObOrNone = User.logIn(request.emailAddress, request.password)
		
		if (not success):
			return LogInUserResponseMessage(errorMessage = errorMessages[authTokOrErrorNum], errorNumber = authTokOrErrorNum)
		return LogInUserResponseMessage(authToken = authTokOrErrorNum, firstName = userObOrNone.firstName, lastName = userObOrNone.lastName, errorNumber = 200)
		
		
	"""
	Logs out a user, deleting their authToken used to validate their login from the database
	On Error: -3, 404
	"""
	@endpoints.method(LogOutUserRequestMessage, LogOutUserResponseMessage, name='logoutUser', path='logoutUser', http_method='POST')    
	def logoutUser(self,request):
		if (request.emailAddress == "") or (request.authToken == ""):
			return LogOutUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		success = User.logOut(request.emailAddress, request.authToken)
		if (success):
			return LogOutUserResponseMessage(errorNumber = 200)
		else:
			return LogOutUserResponseMessage(errorNumber = 404)
		
		
	"""
	Checks to see if the user is logged in (validates the authToken "symbolizing" their log in)
	On Errror: -3, -100
	"""
	@endpoints.method(ValidateUserRequestMessage, ValidateUserResponseMessage, name='validateUser', path='validateUser', http_method='POST')
	def validateUser(self, request):
		if (request.emailAddress == "") or (request.authToken == ""):
			return ValidateUserResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		#validates user
		success, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not success):
			return ValidateUserResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
		return ValidateUserResponseMessage(errorNumber = 200);


	"""
	Generates a new sign up verification token and sends a new verification email to the user associated with the specified
	On Errror: -3, -100
	"""
	@endpoints.method(SendNewEmailVerificationRequestMessage, SendNewEmailVerificationResponseMessage, name='sendNewEmailVerification', path='sendNewEmailVerification', http_method='POST')
	def sendNewEmailVerification(self, request):
		if (request.emailAddress == ""):
			return SendNewEmailVerificationResponseMessage(errorMessage = errorMessages[-3], errorNumber = -3)
		
		#validates user
		success = User.sendVerificationEmail(request.emailAddress)
		if (not success):
			return SendNewEmailVerificationResponseMessage(errorMessage = errorMessages[-4], errorNumber = -4)
		return SendNewEmailVerificationResponseMessage(errorNumber = 200);


	"""
	Sets a Positive rating on on the specified users
	On Errror: -100
	"""
	@endpoints.method(IncrementPositiveRatingRequestMessage, IncrementPositiveRatingResponseMessage, name='incrementPositiveRating', path='incrementPositiveRating', http_method='POST')
	def incrementPositiveRating(self, request):
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return IncrementPositiveRatingResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

		for userKey in request.userKeys:
			Ratings.addPositiveRating(ndb.Key(urlsafe = userKey))
		return IncrementPositiveRatingResponseMessage(errorNumber = 200)


	"""
	Increments a Negative rating on the specified users
	On Errror: -100
	"""
	@endpoints.method(IncrementNegativeRatingRequestMessage, IncrementNegativeRatingResponseMessage, name='incrementNegativeRating', path='incrementNegativeRating', http_method='POST')
	def incrementNegativeRating(self, request):
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return IncrementNegativeRatingResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
		
		for userKey in request.userKeys:
			Ratings.addNegativeRating(ndb.Key(urlsafe = userKey))
		return IncrementNegativeRatingResponseMessage(errorNumber = 200)


	"""
	Adds a report (a complaint) to the specified users
	********
	The reportType integers are:
	0: General Complaint / Other
	1: Harrasment / Bullying
	2: Unfriendly
	********
	On Errror: -3, -100
	"""
	@endpoints.method(AddReportToUserRequestMessage, AddReportToUserResponseMessage, name='addReportToUser', path='addReportToUser', http_method='POST')
	def addReportToUser(self, request):
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return AddReportToUserResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

		for userKey in request.userKeys:
			Ratings.addReportToUser(ndb.Key(urlsafe = userKey), request.reportType, request.comments)
		return AddReportToUserResponseMessage(errorNumber = 200)

	"""
	Adds a compliment to the specified users
	On Errror: -100
	"""
	@endpoints.method(AddComplimentRequestMessage, AddComplimentResponseMessage, name='addCompliment', path='addCompliment', http_method='POST')
	def addCompliment(self, request):
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return AddComplimentResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

		for userKey in request.userKeys:
			Compliment.addCompliment(request.comment, userOb.key, ndb.Key(urlsafe = userKey), ndb.Key(urlsafe = request.mealKey))
		return AddComplimentResponseMessage(errorNumber = 200)

	"""
	Gets the compliments given to the authenticated user
	On Errror: -100
	"""
	@endpoints.method(GetComplimentsGivenToUserRequestMessage, GetComplimentsGivenToUserResponseMessage, name='getComplimentsGivenToUser', path='getComplimentsGivenToUser', http_method='POST')
	def getComplimentsGivenToUser(self, request):
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return GetComplimentsGivenToUserResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

		complimentsList = Compliment.getComplimentsGivenToUser(userOb.key)
		complimentsMessageList = self.convertComplimentsToComplimentMessageList(complimentsList)
		return GetComplimentsGivenToUserResponseMessage(errorNumber = 200, compliments = complimentsMessageList)

	"""
	Gets the compliments given by the authenticated user
	On Errror: -100
	"""
	@endpoints.method(GetComplimentsGivenByUserRequestMessage, GetComplimentsGivenByUserResponseMessage, name='getComplimentsGivenByUser', path='getComplimentsGivenByUser', http_method='POST')
	def getComplimentsGivenByUser(self, request):
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return GetComplimentsGivenByUserResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

		complimentsList = Compliment.getComplimentsGivenByUser(userOb.key)
		complimentsMessageList = self.convertComplimentsToComplimentMessageList(complimentsList)
		return GetComplimentsGivenByUserResponseMessage(errorNumber = 200, compliments = complimentsMessageList)


	

	"""
	Private methods
	"""
	@classmethod
	def convertComplimentsToComplimentMessageList(cls, complimentsList):
		complimentsMessageList = []
		for theCompliment in complimentsList:
			theComplimentMessage = ComplimentMessage(
				toUserKey = theCompliment.receiver.urlsafe(),
				giverUserKey = theCompliment.giver.urlsafe(),
				mealKey = theCompliment.meal.urlsafe(),
				comment = theCompliment.comment
			)
			complimentsMessageList.append(theComplimentMessage)
		return complimentsMessageList
