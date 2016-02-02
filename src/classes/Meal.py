from google.appengine.ext import ndb
from google.appengine.ext.db import TransactionFailedError

import datetime

from Utilities import *
from User import User
from School import School
from Ratings import Ratings

"""
Constant that defines the minimum length in minutes that a meal must be
"""
MINIMUM_MEAL_LENGTH = 30

#unmatched meals are made descendants of school so can get all meals with strong consistency...
#it doesn't matter if getting an indidivuals unmatched meals is only eventually consistent but for matching it does
class UnMatchedMeal(ndb.Model):
    #0 = breakfast, 1 = lunch, 2 = dinner
    mealType = ndb.IntegerProperty(required = True)
    startRange = ndb.DateTimeProperty(required = True)
    endRange = ndb.DateTimeProperty(required = True)
    numPeople = ndb.IntegerProperty(required = True)
    creator = ndb.KeyProperty(required = True, kind = User)
    created = ndb.DateTimeProperty(auto_now_add = True)

    """
    Creates a new unmatched meal for the given user in the database
    Returns [bool of success, meal object or error message]
    """
    @classmethod
    def createNewUnMatchedMeal(cls, userOb, mealType, startRange, endRange, numPeople = 2):
        #check that the user has a verified email and actually has permission to create a meal
        if (not User.hasVerifiedEmail(userOb.emailAddress)):
            return [False, -1]

        #check that the user is in good standing with the community...
        if (not Ratings.userIsInGoodStanding(userOb.key)):
            return [False, -101]

        #get the objects required to create the meal and perform sanity checks
        schoolOb = School.getSchoolObjectByEmail(userOb.emailAddress)

        if (startRange == "" or endRange == ""):
            return [False, -2]
        startTimeOb = stringToDateTimeObject(startRange)
        endTimeOb = stringToDateTimeObject(endRange)
        #meal is long enough to make sense
        if (startTimeOb > endTimeOb - datetime.timedelta(minutes = MINIMUM_MEAL_LENGTH)):
            return [False, -2]
        #meal already happened
        if (startTimeOb <= datetime.datetime.now()):
            return [False, -2]

        if (numPeople < 2):
            return [False, -3]

        if (mealType < 0 or mealType > 2):
            return [False, -4]

        unMealOb = UnMatchedMeal(
            parent = schoolOb.key,
            mealType = mealType,
            startRange = startTimeOb,
            endRange = endTimeOb,
            numPeople = numPeople,
            creator = userOb.key
        )
        unMealOb.put()
        return [True, unMealOb]

    """
    Returns a list of meal objects for the given school
    The list of results is ordered by startTime and broken on ties by createdTime
    """
    @classmethod
    def getAllUnmatchedMealsForSchool(cls, schoolKey):
        return cls.query(ancestor = schoolKey).order(cls.startRange).fetch()

    """
    Gets all the upcoming meals that have been confirmed for a given user
    Returns a list of Meal objects ordered by the date they occur
    """
    @classmethod
    def getUpcomingUnMatchedMealsForUser(cls, userKey):
        nowTime = datetime.datetime.now();
        return cls.query(cls.creator == userKey, cls.startRange >= nowTime).order(cls.startRange).fetch()

    """
    Removes the specified unmatched meal from the database
    Returns: void
    """
    @classmethod
    def removeUnMatchedMeal(cls, unMatchedMealKey):
        unMatchedMealKey.delete()

    """
    Removes the list of specified unmatched meals from the database
    Returns: void
    """
    @classmethod
    def removeUnMatchedMeals(cls, unMatchedMealKeyList):
        if (unMatchedMealKeyList): #only delete keys if the list is not empty
            ndb.delete_multi(unMatchedMealKeyList)



class Meal(ndb.Model):
    #0 = breakfast, 1 = lunch, 2 = dinner
    mealType = ndb.IntegerProperty(required = True)
    startTime = ndb.DateTimeProperty(required = True)
    numPeople = ndb.IntegerProperty(required = True)
    people = ndb.KeyProperty(kind = User, repeated = True)
    matchedDate = ndb.DateTimeProperty(auto_now_add = True)

    """
    Creates a new matched meal from the list of unMatchedMeals
    Before creating the meal, it will be validated that the meal should be created
    and it is possible to create a meal from the two given unmatched meals
    Also deletes the unmatched meals from which the new meal was created
    Returns the created new matched meal if successful or None if it is not
    """
    @classmethod
    def createNewMeal(cls, firstUnMatchedMealObj, secondUnMatchedMealObj):
        #figure out which meal starts first
        earlierMeal = None
        laterMeal = None
        if (firstUnMatchedMealObj.startRange <= secondUnMatchedMealObj.startRange):
            earlierMeal = firstUnMatchedMealObj
            laterMeal = secondUnMatchedMealObj
        else:
            earlierMeal = secondUnMatchedMealObj
            laterMeal = firstUnMatchedMealObj

        #easiest way to determine timing is to just start the new meal at the beginning of the later meal
        newStartTime = laterMeal.startRange
        newPeople = [firstUnMatchedMealObj.creator, secondUnMatchedMealObj.creator]

        #validate the user and make sure that they are actually in good standing with the community
        for person in newPeople:
            if (not Ratings.userIsInGoodStanding(person)):
                return None

        # now we want to put the new meal in the database and 
        mealOb = Meal(
            mealType = firstUnMatchedMealObj.mealType,
            startTime = newStartTime,
            numPeople = len(newPeople),
            people = newPeople
        )

        try:
            cls.__insertNewMeal(mealOb, firstUnMatchedMealObj, secondUnMatchedMealObj)
        except TransactionFailedError:
            return None

        return mealOb

    """
    THIS METHOD SHOULD ONLY BE ACCESSED THROUGH THE createNewMeal method!!
    This method is here only so that the new meal and old meals
    are all inserted and deleted at once in a transaction so that if one fails they all fail
    """
    @classmethod
    @ndb.transactional(xg = True)
    def __insertNewMeal(cls, newMealObj, firstUnMatchedMealObj, secondUnMatchedMealObj):
        newMealObj.put()
        UnMatchedMeal.removeUnMatchedMeals([firstUnMatchedMealObj.key, secondUnMatchedMealObj.key])


    """
    Gets all the upcoming meals that have been confirmed for a given user
    Returns a list of Meal objects ordered by the date they occur
    """
    @classmethod
    def getUpcomingMealsForUser(cls, userKey):
        nowTime = datetime.datetime.now();
        return cls.query(cls.people == userKey, cls.startTime >= nowTime).order(cls.startTime).fetch()

    @classmethod
    def getUpcomingMealsForUserInRange(cls, userKey, startRangeDateOb, endRangeDateOb):
        return cls.query(cls.people == userKey, cls.startTime >= startRangeDateOb, cls.startTime <= endRangeDateOb).order(cls.startTime).fetch()

    """
    Removes the specified matched meal from the database
    Returns: void
    """
    @classmethod
    def removeMeal(cls, mealKey):
        mealKey.delete()

    """
    Removes the list of specified unmatched meals from the database
    Returns: void
    """
    @classmethod
    def removeMeals(cls, mealKeyList):
        if (mealKeyList): #only delete keys if the list is not empty
            ndb.delete_multi(mealKeyList)



