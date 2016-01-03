from google.appengine.ext import ndb

import datetime
# from datetime import timedelta

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
			print("here")
			print(datetime.datetime.now().strftime('%B %d %Y %H:%M:%S'))
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
		#TODO: put back in cls.created after startRange to break ties once sure want that index
		return cls.query(ancestor = schoolKey).order(cls.startRange).fetch()

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
	def removeUnMatchedMeal(cls, unMatchedMealKeyList):
		if (unMatchedMealKeyList): #only delete keys if the list is not empty
			ndb.delete(unMatchedMealKeyList)




# stored as a descendant of the school with all of the people involved in a repeated property
# this works efficiently since each repeated property is stored as a seperate row in the
# entity by property asc table so that cls.people == "1290jd304" returns results extremely efficiently
class Meal(ndb.Model):
	#0 = breakfast, 1 = lunch, 2 = dinner
	mealType = ndb.IntegerProperty(required = True)
	startTime = ndb.DateTimeProperty(required = True)
	numPeople = ndb.IntegerProperty(required = True)
	people = ndb.KeyProperty(kind = User, repeated = True)
	schoolkey = ndb.KeyProperty(required = True, kind = School)
	matchedDate = ndb.DateTimeProperty(auto_now_add = True)

	"""
	Creates a new matched meal from the list of unMatchedMeals
	Returns the created new matched meal if successful or None if it is not
	"""
	@classmethod
	def createNewMatchedMeal(cls, unMatchedMealObjectList):
		if (not unMatchedMealObjectList):
			return F

	"""
	Checks that the two given meal objects could create a valid meal together
	Returns True or False
	"""
	@classmethod
	def canCreateMatchedMeal(cls, firstUnMatchedMealObj, secondUnMatchedMealObj):
		####### These are the meal arrangments that must be accounted for
		#	yes:
		#	1s 2s 1e 2e
		#	2s 1s 2e 1e
		# 	1s 2s 2e 1e
		#	2s 1s 1e 2e
		#	no:
		#	1s 1e 2s 2e
		#	2s 2e 1s 1e
		######

		#CHECK MEAL TYPE
		if (firstUnMatchedMealObj.mealType != secondUnMatchedMealObj.mealType):
			return False

		#CHECK TIMING
		#the important part is just to determine the overlap.. so figure out which meal starts first
		earlierMeal = None
		laterMeal = None
		if (firstUnMatchedMealObj.startRange <= secondUnMatchedMealObj.startRange):
			earlierMeal = firstUnMatchedMealObj
			laterMeal = secondUnMatchedMealObj
		else:
			earlierMeal = secondUnMatchedMealObj
			laterMeal = firstUnMatchedMealObj

		#just need to make sure the later meal starts at least 30 minutes before the earlier meal ends 
		#if this is the case, then have an overlap of the minimum length necessary between the meals
		if (earlierMeal.endRange - datetime.timedelta(minutes = MINIMUM_MEAL_LENGTH) < laterMeal.startRange):
			return False

		###################
		#  This should come last as it involves a database call!
		##################
		#CHECK COMMUNITY STANDING 
		#lets verify that both creators of the meals are in good standing with the community
		if (not Ratings.userIsInGoodStanding(firstUnMatchedMealObj.creator)):
			return False
		if (not Ratings.userIsInGoodStanding(secondUnMatchedMealObj.creator)):
			return False

		#if made it to this point everything looks good!
		return True
















##########################################
#
# THIS IS IT - all unmatched meals are descendants of the school and will just have a userid column for the person who started it
# so to find someones unmatched meals just search for userkey == user and limit to descendants of the correct school (this is fine cause sorted by property in the table)
#
# and then when cron job is run, we have to get all unmatchedmeal descendants of a school
#
#
# IN THE CRON JOB:
# first get all descendants (sort by time created)
# linearly scan through all of the descendants and delete (actually add to a list) any of the meals that are past time (should send a notification saying sorry no one wanted to eat with you.. OH THIS COULD BE HOW I TEST NOTIFICATIONS!!!)
# now, the algorithm only deals in 15 minute increments... create a hashtable of all meals at that school for each 15 minute block and place all meals corresponding to each block (their start time) in order in the bucket and each bucket is really a queue
#	at some point along here need to check that the user is in good standing for making a meal
# now, go through from the start to end since people can eat later but later people can't eat earlier and for each meal
# now for each meal, get the next meal from those buckets which are endTime - 30 of currentMeal (we know that the person can eat it has to be at least 30 minutes long)
# if we find a match, create a matched meal and append it to the list (in the end the whole list will be committed at once)
# then go through the whole list and send out the notifications that we need to send
# now do delete all deleteable meals at once
# go through whole list and send out notifications for those deleted meals
#
#
# Plan of action going forward
# get basic meal api done (add unmatched meal)
# create the cron job
# add matched meals in the cron job
##########################################

