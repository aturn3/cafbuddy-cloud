from google.appengine.ext import ndb

from Utilities import *

class School(ndb.Model):
	name = ndb.StringProperty() #This is our best guess at a name unless it is set explicitly. Initially it is just set by taking the part between @ and . in the email.
	emailDomain = ndb.StringProperty() # This is the non-name part of the email. E.g. @wisc.edu or @stolaf.edu
	created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)

	"""
	Creates a school object and puts it in the database
	Guesses the name of the school based off of the given email address
	The given email address can be email address of any student at that school
	Returns [bool, schoolOb or None] depending on success
	"""
	@classmethod
	def createOrGetSchoolObjectByEmail(cls, emailAddress):
		(success, emailDomain) = getEmailDomainFromEmailAddress(emailAddress)
		if (not success):
			return [False, None]
		schoolNameEndIndx = emailDomain.rfind(".")
		schoolName = emailDomain[1:schoolNameEndIndx]
		# make sure the school wasn't already created
		schoolOb = cls.getSchoolObjectByEmail(emailAddress)
		if (schoolOb is not None):
			return [True, schoolOb]
		schoolOb = School(name = schoolName, emailDomain = emailDomain)
		schoolOb.put()
		return [True, schoolOb]

	"""
	Gets a school object by any email address associated with that school
	Returns the school object if it is found, otherwise it returns None
	"""
	@classmethod
	def getSchoolObjectByEmail(cls, emailAddress):
		(success, emailDomain) = getEmailDomainFromEmailAddress(emailAddress)
		if (not success):
			return None
		return School.query(School.emailDomain == emailDomain).get()
