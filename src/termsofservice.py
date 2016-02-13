import webapp2

class TermsOfService(webapp2.RequestHandler):
    def get(self):

        theTermsOfService = """
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n      
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        This is some terms of service\n
        """
        self.response.write(theTermsOfService)


application = webapp2.WSGIApplication([('/termsofservice', TermsOfService)], debug = False)


