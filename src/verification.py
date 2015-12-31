import webapp2

from classes.User import User

class EmailVerifier(webapp2.RequestHandler):
    def get(self):
    	emailAddress = self.request.get('email')
    	signupToken = self.request.get('signupTok')
    	if (User.verifyEmail(emailAddress, signupToken)):
    		self.response.write("Success. Your email " + emailAddress + " has been successfully verified. Get ready to meet tons of new people!")
    	else:
    		self.response.write("Oh no! Something went wrong and we weren't able to verify the email " + emailAddress + ". Please try again by using the app to send a new verification email.")


application = webapp2.WSGIApplication([('/verifyemail', EmailVerifier)], debug = False)
