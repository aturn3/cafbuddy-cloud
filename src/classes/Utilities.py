"""
This file contains miscellaneous functions used throughout the APIs and classes
"""
import datetime

"""
Capitalizes the first letter of every word in the name
and lowercases the rest. Also capitalizes the first
letter after a hyphen
"""
def cleanUpName(name):
	if (name == ""):
		return name
	byWord = name.split()
	newName = ""
	for word in byWord:
		partialWords = word.split("-")
		word = ""
		for partialWord in partialWords:
			partialWord = partialWord.capitalize()
			word += "-" + partialWord
		word = word[1:]
		newName += " " + word
	return newName[1:]

"""
Gets the domain of the email address from any given address
Also performs some clean up on the email address to ensure that
the domain is always the same (lowercases everything)
Returns a tupple [bool, domain] indicating if the email address
was valid and a real domain was extracted from it
"""
def getEmailDomainFromEmailAddress(emailAddress):
	emailAddress = emailAddress.lower()
	if ("@" not in emailAddress or "." not in emailAddress):
	    return [False, ""]
	emailDomainIndx = emailAddress.find("@")
	emailDomain = emailAddress[emailDomainIndx:]
	return [True, emailDomain]

"""
Standard utility function used to convert strings received from the client into a datetime
object in order to store it in the database
Expects string in format 'Month Day Year Hour(24):Minute:Second' (e.g. 'January 03 2016 00:43:58')
"""
def stringToDateTimeObject(str):
	return datetime.datetime.strptime(str, '%B %d %Y %H:%M:%S')

"""
Standard utility function used to convert datetime objects in the database into the standard
format string expected by the client
Returns string in format 'Month Day Year Hour(24):Minute:Second' (e.g. 'January 03 2016 00:43:58')
"""
def dateTimeOjectToString(dateTimeOb):
	return dateTimeOb.strftime('%B %d %Y %H:%M:%S')