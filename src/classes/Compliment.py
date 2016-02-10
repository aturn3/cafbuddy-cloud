from google.appengine.ext import ndb

from User import User
from Meal import Meal

# this is a descendant of the user
class Compliment(ndb.Model):
	comment = ndb.StringProperty(required = True, indexed = False)
	giver = ndb.KeyProperty(required = True, kind = User, indexed = True)
	receiver = ndb.KeyProperty(required = True, kind = User, indexed = True)
	meal = ndb.KeyProperty(required = True, kind = Meal, indexed = True)
	added = ndb.DateTimeProperty(auto_now_add = True)
	

	"""
	Adds a compliment to a given user from a given user for a given meal
	Returns: void
	"""
	@classmethod
	def addCompliment(cls, theComment, fromUserKey, toUserKey, mealkey):
		complimentOb = Compliment(
			receiver = toUserKey,
			comment = theComment,
			meal = mealkey,
			giver = fromUserKey
		)
		complimentOb.put()

	"""
	Gets all of the compliments given to a specific user
	Returns: a list of compliemtn objects ordered by date
	"""
	@classmethod
	def getComplimentsGivenToUser(cls, userKey):
		return cls.query(cls.receiver == userKey).order(cls.added).fetch()

	"""
	Gets all of the compliments given by a specific user
	Returns: a list of the compliment objects ordered by date
	"""
	@classmethod
	def getComplimentsGivenByUser(cls, userKey):
		return cls.query(cls.giver == userKey).order(cls.added).fetch()