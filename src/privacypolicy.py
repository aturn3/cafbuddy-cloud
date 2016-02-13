import webapp2

class PrivacyPolicy(webapp2.RequestHandler):
    def get(self):

        thePrivacyPolicy = """
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        This is some privacy policy\n
        """
        self.response.write(thePrivacyPolicy)


application = webapp2.WSGIApplication([('/privacypolicy', PrivacyPolicy)], debug = False)


