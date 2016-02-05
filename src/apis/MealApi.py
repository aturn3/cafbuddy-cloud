import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from classes.Meal import *
from classes.User import User
from classes.Utilities import *


"""
Application Specific Error Numbers
-1 => User has not validated their email yet
-2 => The start and end times were invalid
-3 => At least two people are required for a meal
-4 => Invalid meal type ( < 0 or > 2)
-5 => Note a valid date range
-100 => User was unable to be validated as logged in
-101 => User is not in good standing with the community (was reported / downvoted)
"""

#The error messages that will be returned to their client and displayed to the user.
errorMessages = {
    -1: "You must verify your email in order to create a new meal.",
    -2: "That is not a valid start and/or end meal time. Note that at least 30 minutes must be set aside for a meal.",
    -3: "There must be at least two people to have a meal.",
    -4: "That is not a valid meal type.",
    -5: "That is not a valid date range.",
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

class GetUpcomingMatchedMealsRequestMessage(messages.Message):
    authToken = messages.StringField(1, required = True)
    emailAddress = messages.StringField(2, required = True)

class GetUpcomingUnMatchedMealsRequestMessage(messages.Message):
    authToken = messages.StringField(1, required = True)
    emailAddress = messages.StringField(2, required = True)

class GetAllUpcomingMealsRequestMessage(messages.Message):
    authToken = messages.StringField(1, required = True)
    emailAddress = messages.StringField(2, required = True)

class GetMatchedMealsInRangeRequestMessage(messages.Message):
    authToken = messages.StringField(1, required = True)
    emailAddress = messages.StringField(2, required = True)
    startRange = messages.StringField(3, required = True)
    endRange = messages.StringField(4, required = True)

class DeleteUnMatchedMealRequestMessage(messages.Message):
    authToken = messages.StringField(1, required = True)
    emailAddress = messages.StringField(2, required = True)
    mealKey = messages.StringField(3, required = True)

class EditUnMatchedMealRequestMessage(messages.Message):
    authToken = messages.StringField(1, required = True)
    emailAddress = messages.StringField(2, required = True)
    mealKey = messages.StringField(3, required = True)
    mealType = messages.IntegerField(4, required = False)
    startRange = messages.StringField(5, required = False)
    endRange = messages.StringField(6, required = False)
    numPeople = messages.IntegerField(7, required = False)

"""
Response ProtoRPC message classes
"""
class UnMatchedMealMessage(messages.Message):
    mealType = messages.IntegerField(1, required = True)
    startRange = messages.StringField(2, required = True)
    endRange = messages.StringField(3, required = True)
    numPeople = messages.IntegerField(4, required = True)
    created = messages.StringField(5, required = True)
    creatorKey = messages.StringField(6, required = True)
    mealKey = messages.StringField(7, required = True)

class MatchedMealMessage(messages.Message):
    mealType = messages.IntegerField(1, required = True)
    startTime = messages.StringField(2, required = True)
    numPeople = messages.IntegerField(3, required = True)
    peopleKeys = messages.StringField(4, repeated = True)
    matchedDate = messages.StringField(5, required = True)
    mealKey = messages.StringField(6, required = True)

"""
Response ProtoRPC messages
""" 
class CreateNewMealResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)
    mealKey = messages.StringField(3, required = False)

class GetUpcomingMatchedMealsResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)
    matchedMeals = messages.MessageField(MatchedMealMessage, 3, repeated = True)

class GetUpcomingUnMatchedMealsResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)
    unMatchedMeals = messages.MessageField(UnMatchedMealMessage, 3, repeated = True)

class GetAllUpcomingMealsResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)
    matchedMeals = messages.MessageField(MatchedMealMessage, 3, repeated = True)
    unMatchedMeals = messages.MessageField(UnMatchedMealMessage, 4, repeated = True)

class GetMatchedMealsInRangeResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)
    matchedMeals = messages.MessageField(MatchedMealMessage, 3, repeated = True)

class DeleteUnMatchedMealResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)

class EditUnMatchedMealResponseMessage(messages.Message):
    errorNumber = messages.IntegerField(1, required = False)
    errorMessage = messages.StringField(2, required = False)


@endpoints.api(name='mealService', version='v1.0', description='API for dealing with meals', hostname='cafbuddy.appspot.com')  
class MealApi(remote.Service):

    """
    Creates a new unmatched meal that will try to be matched with someone else
    startRange and endRange must be given in UTC time. They must be of the format:
    'Month Day Year Hour(24):Minute:Second' (e.g. 'January 03 2016 00:43:58')
    On Error: -1, -2, -3, -4, -100, -101
    """
    @endpoints.method(CreateNewMealRequestMessage, CreateNewMealResponseMessage, name='createNewMeal', path='createNewMeal', http_method='POST')
    def createNewMeal(self, request):        
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return CreateNewMealResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
        
        success, errorNumOrMealOb = UnMatchedMeal.createNewUnMatchedMeal(userOb, request.mealType, request.startRange, request.endRange, request.numPeople)
        if (not success):
            return CreateNewMealResponseMessage(errorMessage = errorMessages[errorNumOrMealOb], errorNumber = errorNumOrMealOb)
        return CreateNewMealResponseMessage(errorNumber = 200, mealKey = errorNumOrMealOb.key.urlsafe())


    """
    Gets all the upcoming meals for the validated user that are still waiting to try and find a match
    On Error: -100 
    """
    @endpoints.method(GetUpcomingMatchedMealsRequestMessage, GetUpcomingMatchedMealsResponseMessage, name='getUpcomingMatchedMeals', path='getUpcomingMatchedMeals', http_method='POST')
    def getUpcomingMatchedMeals(self, request):        
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return GetUpcomingMatchedMealsResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
        
        upcomingMealsList = Meal.getUpcomingMealsForUser(userOb.key)
        matchedMealsMessageList = self.convertMatchedListToMatchedMessageList(upcomingMealsList)

        return GetUpcomingMatchedMealsResponseMessage(errorNumber = 200, matchedMeals = matchedMealsMessageList)

    """
    Gets all the upcoming unmatched meals for the validated user (potential meals which have yet to be matched with others)
    On Error: -100
    """
    @endpoints.method(GetUpcomingUnMatchedMealsRequestMessage, GetUpcomingUnMatchedMealsResponseMessage, name='getUpcomingUnMatchedMeals', path='getUpcomingUnMatchedMeals', http_method='POST')
    def getUpcomingUnMatchedMeals(self, request):        
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return GetUpcomingUnMatchedMealsResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
        
        upcomingUnMatchedMealsList = UnMatchedMeal.getUpcomingUnMatchedMealsForUser(userOb.key)
        unMatchedMealsMessageList = self.convertUnMatchedListToUnMatchedMessageList(upcomingUnMatchedMealsList)

        return GetUpcomingUnMatchedMealsResponseMessage(errorNumber = 200, unMatchedMeals = unMatchedMealsMessageList)


    """
    Combines the getUpcomingMatchedMeals and getUpcomingUnMatchedMeals API calls by returning all the upcoming
    matched and unmatched meals
    On Error: -100
    """
    @endpoints.method(GetAllUpcomingMealsRequestMessage, GetAllUpcomingMealsResponseMessage, name='getAllUpcomingMeals', path='getAllUpcomingMeals', http_method='POST')
    def getAllUpcomingMeals(self, request):
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return GetAllUpcomingMealsResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
        
        upcomingMealsList = Meal.getUpcomingMealsForUser(userOb.key)
        upcomingUnMatchedMealsList = UnMatchedMeal.getUpcomingUnMatchedMealsForUser(userOb.key)

        matchedMealsMessageList = self.convertMatchedListToMatchedMessageList(upcomingMealsList)
        unMatchedMealsMessageList = self.convertUnMatchedListToUnMatchedMessageList(upcomingUnMatchedMealsList)

        return GetAllUpcomingMealsResponseMessage(errorNumber = 200, matchedMeals = matchedMealsMessageList, unMatchedMeals = unMatchedMealsMessageList)

    """
    Gets all the matched meals (meals that have been paired with others) within the specified date range
    On Error: -5, -100
    """
    @endpoints.method(GetMatchedMealsInRangeRequestMessage, GetMatchedMealsInRangeResponseMessage, name='getMatchedMealsInRange', path='getMatchedMealsInRange', http_method='POST')
    def getMatchedMealsInRange(self, request):
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return GetMatchedMealsInRangeResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)
        
        startRangeDateOb = stringToDateTimeObject(request.startRange)
        endRangeDateOb = stringToDateTimeObject(request.endRange)
        if (startRangeDateOb > endRangeDateOb):
            return GetMatchedMealsInRangeResponseMessage(errorMessage = errorMessages[-5], errorNumber = -5)

        mealListInRange = Meal.getUpcomingMealsForUserInRange(userOb.key, startRangeDateOb, endRangeDateOb)
        mealsInRangeMessageList = self.convertMatchedListToMatchedMessageList(mealListInRange)

        return GetMatchedMealsInRangeResponseMessage(errorNumber = 200, matchedMeals = mealsInRangeMessageList)

    """
    Deletes the specified unmatched meal
    On Error: -100 
    """
    @endpoints.method(DeleteUnMatchedMealRequestMessage, DeleteUnMatchedMealResponseMessage, name='deleteUnMatchedMeal', path='deleteUnMatchedMeal', http_method='POST')
    def deleteUnMatchedMeal(self, request):
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return DeleteUnMatchedMealResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

        UnMatchedMeal.removeUnMatchedMeal(ndb.Key(urlsafe=request.mealKey))

        return DeleteUnMatchedMealResponseMessage(errorNumber = 200)

    """
    Edits the specified unmatched meal
    On Error: -100, -2, -3, -4
    """
    @endpoints.method(EditUnMatchedMealRequestMessage, EditUnMatchedMealResponseMessage, name='editUnMatchedMeal', path='editUnMatchedMeal', http_method='POST')
    def editUnMatchedMeal(self, request):
        isLoggedIn, userOb = User.validateLogIn(request.emailAddress, request.authToken)
        if (not isLoggedIn):
            return EditUnMatchedMealResponseMessage(errorMessage = errorMessages[-100], errorNumber = -100)

        # assume that none of them should be edited
        theMealType = None
        theStartRange = None
        theEndRange = None
        theNumPeople = None

        #if they should be edited
        if (request.mealType != None):
            theMealType = request.mealType
        if (request.startRange != None):
            theStartRange = stringToDateTimeObject(request.startRange)
        if (request.endRange != None):
            theEndRange = stringToDateTimeObject(request.endRange)
        if (request.numPeople != None):
            theNumPeople = request.numPeople
        
        success, errorNum = UnMatchedMeal.editUnMatchedMeal(ndb.Key(urlsafe=request.mealKey), mealType = theMealType, startRange = theStartRange, endRange = theEndRange, numPeople = theNumPeople)

        if (not success):
            return EditUnMatchedMealResponseMessage(errorMessage = errorMessages[errorNum], errorNumber = errorNum)
        return EditUnMatchedMealResponseMessage(errorNumber = 200)


    """
    Private methods
    """

    @classmethod
    def convertUnMatchedListToUnMatchedMessageList(cls, unMatchedMealsList):
        unMatchedMealsMessageList = []
        for theMeal in unMatchedMealsList:
            theUnMatchedMatchedMeal = UnMatchedMealMessage(
                mealType = theMeal.mealType,
                startRange = dateTimeOjectToString(theMeal.startRange),
                endRange = dateTimeOjectToString(theMeal.endRange),
                numPeople = theMeal.numPeople,
                created = dateTimeOjectToString(theMeal.created),
                creatorKey = theMeal.creator.urlsafe(),
                mealKey = theMeal.key.urlsafe()
            )
            unMatchedMealsMessageList.append(theUnMatchedMatchedMeal)
        return unMatchedMealsMessageList

    @classmethod
    def convertMatchedListToMatchedMessageList(cls, matchedMealsList):
        matchedMealsMessageList = []
        for theMeal in matchedMealsList:
            theMatchedMeal = MatchedMealMessage(
                mealType = theMeal.mealType,
                startTime = dateTimeOjectToString(theMeal.startTime),
                numPeople = theMeal.numPeople,
                peopleKeys = [personKey.urlsafe() for personKey in theMeal.people],
                matchedDate = dateTimeOjectToString(theMeal.matchedDate),
                mealKey = theMeal.key.urlsafe()
            )
            matchedMealsMessageList.append(theMatchedMeal)
        return matchedMealsMessageList


"""
    def getMealsInRange()
    """