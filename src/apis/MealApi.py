import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from classes.Meal import UnMatchedMeal
from classes.User import User


"""
Application Specific Error Numbers
-1 => User has not validated their email yet
-2 => The start and end times were invalid
-3 => At least two people are required for a meal
-4 => Invalid meal type ( < 0 or > 2)
-100 => User was unable to be validated as logged in
-101 => User is not in good standing with the community (was reported / downvoted)
"""

#The error messages that will be returned to their client and displayed to the user.
errorMessages = {
	-1: "You must verify your email in order to create a new meal.",
	-2: "That is not a valid start and/or end meal time. Note that at least 30 minutes must be set aside for a meal.",
	-3: "There must be at least two people to have a meal.",
	-4: "That is not a valid meal type.",
	-100: "You are not logged in.",
	-101: "You have been reported negatively by the community. Please contact CafBuddy directly to continue enjoying these services."
}


"""
Request ProtoRPC messages
"""
class CreateNewMealRequestMessage(messages.Message):
	authToken = messages.StringField(1, required = True)
	emailAddress = messages.StringField(2, required = True)
	mealType = messages.IntegerField(3, required = True)
	startRange = messages.StringField(4, required = True)
	endRange = messages.StringField(5, required = True)
	numPeople = messages.IntegerField(6, required = True)

"""
Response ProtoRPC messages
"""	
class CreateNewMealResponseMessage(messages.Message):
	errorNumber = messages.IntegerField(1, required = False)
	errorMessage = messages.StringField(2, required = False)
	mealKey = messages.StringField(3, required = False)



@endpoints.api(name='mealService', version='v1.0', description='API for dealing with meals', hostname='cafbuddy.appspot.com')  
class MealApi(remote.Service):

	"""
	Creates a new unmatched meal
	startRange and endRange must be given in UTC time. They must be of the format:
	'Month Day Year Hour(24):Minute:Second' (e.g. 'January 03 2016 00:43:58')
	On Error: -1, -2, -3, -4, -101
	"""
	@endpoints.method(CreateNewMealRequestMessage, CreateNewMealResponseMessage, name='createNewMeal', path='createNewMeal', http_method='POST')
	def createNewMeal(self, request):        
		isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
		if (not isLoggedIn):
			return AddReportToUserResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
		
		success, errorNumOrMealOb = UnMatchedMeal.createNewUnMatchedMeal(userOb, request.mealType, request.startRange, request.endRange, request.numPeople)
		if (not success):
			return CreateNewMealResponseMessage(errorMessage = errorMessages[errorNumOrMealOb], errorNumber = errorNumOrMealOb)
		return CreateNewMealResponseMessage(errorNumber = 200, mealKey = errorNumOrMealOb.key.urlsafe())


"""
getUpcomingMatchedMeals() - returns all the upcoming matched meals
getUpcomingUnMatchedMeals() - returns all the upcoming unmatched meals for a user
createNewMeal()
"""