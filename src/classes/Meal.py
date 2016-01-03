from google.appengine.ext import ndb

import datetime
# from datetime import timedelta

from Utilities import *
from classes.User import User
from classes.School import School
from classes.Ratings import Ratings

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



#each user has a copy of the meal as a descendant since the most important thing at this point is just easy access
#to upcoming meals for the user
class Meal(ndb.Model):
	#0 = breakfast, 1 = lunch, 2 = dinner
	mealType = ndb.IntegerProperty(required = True)
	startTime = ndb.DateTimeProperty(required = True)
	numPeople = ndb.IntegerProperty(required = True)
	people = ndb.KeyProperty(kind = User, repeated = True)
	schoolkey = ndb.KeyProperty(required = True, kind = School)
	matchedDate = ndb.DateTimeProperty(auto_now_add = True)



#check if the user has permission to create a meal (is verified email account)
#check that the user is in good standing (ratings - do we actually want to store date so can know)
#check if any of the current unmatched meals will satisfy the current meal request
#create the meal for the user
















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

