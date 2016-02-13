import webapp2

class Credits(webapp2.RequestHandler):
    def get(self):

        theCredits = """
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        This is some credits\n
        """
        self.response.write(theCredits)


application = webapp2.WSGIApplication([('/credits', Credits)], debug = False)


