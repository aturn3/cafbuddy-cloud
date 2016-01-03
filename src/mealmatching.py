import webapp2

from classes.School import School
from classes.Meal import UnMatchedMeal
from classes.Utilities import *


class MatchMeals(webapp2.RequestHandler):
    def get(self):
    	#perform the algorithm one at a time on the schools
    	schools = School.getAllSchoolObjects()
    	for school in schools:
    		unmatchedMeals = UnMatchedMeal.getAllUnmatchedMealsForSchool(school.key)
    		for unmeal in unmatchedMeals:
	    		print("\n" + "Meal Type : ")
	    		print(unmeal.mealType)
	    		print("   " + dateTimeOjectToString(unmeal.startRange) + " - " + dateTimeOjectToString(unmeal.endRange) + "     Created: " + dateTimeOjectToString(unmeal.created))
    		# self.response.write("\n" + school.name + " : The domain is " + school.emailDomain)
    	

    	# emailAddress = self.request.get('email')
    	# signupToken = self.request.get('signupTok')
    	# if (User.verifyEmail(emailAddress, signupToken)):
    	# 	self.response.write("Success. Your email " + emailAddress + " has been successfully verified. Get ready to meet tons of new people!")
    	# else:
    	# 	self.response.write("Oh no! Something went wrong and we weren't able to verify the email " + emailAddress + ". Please try again by using the app to send a new verification email.")


application = webapp2.WSGIApplication([('/mealmatching', MatchMeals)], debug = False)
