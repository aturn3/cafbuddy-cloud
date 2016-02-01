from google.appengine.ext import ndb
import datetime

from Utilities import *


class Report(ndb.Model):
	reportType = ndb.IntegerProperty(required = True, indexed = False)
	comments = ndb.StringProperty(indexed = False)
	created = ndb.DateTimeProperty(auto_now_add = True)


class Ratings(ndb.Model):
	positiveRatings = ndb.IntegerProperty(required = True, indexed = False)
	negativeRatings = ndb.IntegerProperty(required = True, indexed = False)
	positiveRatingsDates = ndb.DateTimeProperty(repeated = True, indexed = False)
	negativeRatingsDates = ndb.DateTimeProperty(repeated = True, indexed = False)
	reports = ndb.StructuredProperty(Report, repeated = True, indexed = False)


	"""
	Validates that a user is in good standing with the community
	Returns true always currently
	"""
	@classmethod
	def userIsInGoodStanding(cls, userKey):
		return True

	"""
	Adds a positive rating to the to the user specified by the given userKey
	"""
	@classmethod
	def addPositiveRating(cls, userKey):
		ratingOb = cls.getOrCreateRatingsObjectForUser(userKey)
		ratingOb.positiveRatings += 1
		ratingOb.positiveRatingsDates.append(datetime.datetime.now())
		ratingOb.put()

	"""
	Adds a negative rating to the to the user specified by the given userKey
	"""
	@classmethod
	def addNegativeRating(cls, userKey):
		ratingOb = cls.getOrCreateRatingsObjectForUser(userKey)
		ratingOb.negativeRatings += 1
		ratingOb.negativeRatingsDates.append(datetime.datetime.now())
		ratingOb.put()	

	"""
	Adds a report (bad) to the user specified in the userKey
	"""
	@classmethod
	def addReportToUser(cls, userOb, reportType, comments = ""):
		# first lets email Turnblad and I
		# mailSender = "Caf Buddy <noreply@cafbuddy.appspotmail.com>"
		# mailTo = "jforster959@gmail.com, aturnblad3@gmail.com"
		# mailSubject = "User " + userOb.firstName + " " + userOb.lastName + " Was Reported"
		# mailBody = "User " + userOb.firstName + " " + userOb.lastName + ""  "" ",\n\n Welcome to Caf Buddy!"
		# mailBody += "\n\n We just need to make sure you are part of the St. Olaf community, so you just need to quickly verify your account."
		# mailBody += " Click the following link or copy and paste it into your favorite browser and you will be all set to meet tons of new people and never eat alone again."
		# mailBody += "\n\n http://cafbuddy.appspot.com/verifyemail?email=" + emailAddress + "&signupTok=" + signupToken
		# mailBody += "\n\n If you did not sign up for Caf Buddy or were not expecting this email then you can safely ignore it."
		# mail.send_mail(
		# 	sender = mailSender,
		# 	to = mailTo,
		# 	subject = mailSubject,
		# 	body = mailBody
		# )

		# then lets add the report to the user
		ratingOb = cls.getOrCreateRatingsObjectForUser(userOb.key)
		newReport = Report(
			reportType = reportType,
			comments = comments
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
				positiveRatings = 0,
				negativeRatings = 0,
				positiveRatingsDates = [],
				negativeRatingsDates = [],
				reports = []
			)
			ratingOb.put()
		return ratingOb


