from google.appengine.ext import ndb
from google.appengine.api import mail
import datetime

from Utilities import *

from Meal import Meal
from User import User


class Report(ndb.Model):
	reportType = ndb.IntegerProperty(required = True, indexed = True)
	comments = ndb.StringProperty(indexed = False)
	giver = ndb.KeyProperty(required = True, kind = User, indexed = True)
	meal = ndb.KeyProperty(required = True, kind = Meal, indexed = True)
	added = ndb.DateTimeProperty(auto_now_add = True)

class Rating(ndb.Model):
	meal = ndb.KeyProperty(required = True, kind = Meal, indexed = True)
	giver = ndb.KeyProperty(required = True, kind = User, indexed = True)
	added = ndb.DateTimeProperty(auto_now_add = True)

# the aggregate object that is actually assigned to the user
class Ratings(ndb.Model):
	numPositiveRatings = ndb.IntegerProperty(required = True, indexed = True)
	numNegativeRatings = ndb.IntegerProperty(required = True, indexed = True)
	negativeRatings = ndb.StructuredProperty(Rating, repeated = True, indexed = True)
	positiveRatings = ndb.StructuredProperty(Rating, repeated = True, indexed = True)
	reports = ndb.StructuredProperty(Report, repeated = True, indexed = True)


	"""
	Validates that a user is in good standing with the community
	Returns true always currently
	"""
	@classmethod
	def userIsInGoodStanding(cls, userKey):
		return True

	"""
	Adds a positive rating to the to the user specified by the given userKey
	given by the user specified in the raterUserKey for the meal in the mealKey
	"""
	@classmethod
	def addPositiveRating(cls, userKey, mealKey, raterUserKey):
		ratingOb = cls.getOrCreateRatingsObjectForUser(userKey)
		ratingOb.numPositiveRatings += 1
		newRating = Rating(
			meal = mealKey,
			giver = raterUserKey
		)
		ratingOb.positiveRatings.append(newRating)
		ratingOb.put()

	"""
	Adds a negative rating to the to the user specified by the given userKey
	given by the user specified in the raterUserKey for the meal in the mealKey
	"""
	@classmethod
	def addNegativeRating(cls, userKey, mealKey, raterUserKey):
		ratingOb = cls.getOrCreateRatingsObjectForUser(userKey)
		ratingOb.numNegativeRatings += 1
		newRating = Rating(
			meal = mealKey,
			giver = raterUserKey
		)
		ratingOb.negativeRatings.append(newRating)
		ratingOb.put()	

	"""
	Adds a report (bad) to the user specified in the userKey
	"""
	@classmethod
	def addReportToUser(cls, userKey, reportType, fromUserKey, mealKey, comments = ""):
		userOb = User.getUserObjectForkey(userKey)

		# first lets email Turnblad and I
		mailSender = "Caf Buddy <noreply@cafbuddy.appspotmail.com>"
		mailTo = "jforster959@gmail.com, aturnblad3@gmail.com"
		mailSubject = "User " + userOb.firstName + " " + userOb.lastName + " Was Reported"
		mailBody = "User " + userOb.firstName + " " + userOb.lastName + " was reported at about " + dateTimeOjectToString(datetime.datetime.now()) + ". The comments read:\n" + comments + "\nCheck the datastore to see more information."
		mail.send_mail(
			sender = mailSender,
			to = mailTo,
			subject = mailSubject,
			body = mailBody
		)

		# then lets add the report to the user
		ratingOb = cls.getOrCreateRatingsObjectForUser(userKey)
		newReport = Report(
			reportType = reportType,
			comments = comments,
			giver = fromUserKey,
			meal = mealKey
		)
		ratingOb.reports.append(newReport)
		ratingOb.put()

	"""
	Gets the ratings object for a given user if it already exists
	Otherwise, if one does not yet exist, it creates a rating object for the user
	Returns the rating object
	"""
	@classmethod
	def getOrCreateRatingsObjectForUser(cls, userKey):	
		ratingOb = cls.query(ancestor = userKey).get()
		if (ratingOb is None):
			ratingOb = Ratings(
				parent = userKey,
				numPositiveRatings = 0,
				numNegativeRatings = 0,
				positiveRatings = [],
				negativeRatings = [],
				reports = []
			)
			ratingOb.put()
		return ratingOb


