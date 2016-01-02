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
	def addReportToUser(cls, userKey, reportType, comments = ""):
		ratingOb = cls.getOrCreateRatingsObjectForUser(userKey)
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


