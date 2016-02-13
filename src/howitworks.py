import webapp2

class HowItWorks(webapp2.RequestHandler):
    def get(self):

        theExplanation = """
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        This is how it works\n
        """
        self.response.write(theExplanation)


application = webapp2.WSGIApplication([('/howitworks', HowItWorks)], debug = False)


