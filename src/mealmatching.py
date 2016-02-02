import webapp2

import datetime

from classes.Utilities import *
from classes.School import School
from classes.Meal import *
from classes.User import User


class MatchMeals(webapp2.RequestHandler):
    def get(self):
        currentTime = datetime.datetime.now()
        #perform the algorithm one at a time on the schools
        schools = School.getAllSchoolObjects()
        for school in schools:
            #get all the meals for a particular school and go through meals one by one
            unMatchedMealsToDelete = []
            unMatchedMealsToMatch = []
            unMatchedMeals = UnMatchedMeal.getAllUnmatchedMealsForSchool(school.key)
            indx = 0
            numUnMatchedMeals = len(unMatchedMeals)
            while (indx < numUnMatchedMeals):
                #if the meal has already "happened" but never got matched, we should delete it, so add it to the list
                if (unMatchedMeals[indx].endRange < currentTime):
                    unMatchedMealsToDelete.append(unMatchedMeals[indx])
                    indx += 1
                #else lets try to match this meal
                else:
                    numMatched = 1 #number of meals matched with this meal so far
                    searchIndx = indx + 1 #current meal trying to match with this meal
                    matchedMeals = [] #the meals and their index that we have matched with this meal so far
                    # continue while we have fewer matched meals than we want, we haven't gone through all unmatched meals
                    # and we haven't hit the point where any meals after that wont match because their start time is later than
                    # the end time of the meal we are looking at minus the minimum length of a meal
                    while (numMatched < unMatchedMeals[indx].numPeople and searchIndx < numUnMatchedMeals and (unMatchedMeals[indx].endRange - datetime.timedelta(minutes = MINIMUM_MEAL_LENGTH)) > unMatchedMeals[searchIndx].startRange):
                        mealTypesMatch = (unMatchedMeals[indx].mealType == unMatchedMeals[searchIndx].mealType)
                        numPeopleMatch = (unMatchedMeals[searchIndx].numPeople == unMatchedMeals[indx].numPeople)
                        # notSameCreator = (unMatchedMeals[searchIndx].creator != unMatchedMeals[indx].creator)
                        if (mealTypesMatch and numPeopleMatch):
                            numMatched += 1
                            matchedMeals.append([searchIndx, unMatchedMeals[searchIndx]])
                        searchIndx += 1

                    #if successfully was able to find matches for a given meal... then add those unmatched meals to be turned into meals later
                    if (numMatched >= unMatchedMeals[indx].numPeople):
                        listToAddToMealsToMatch = [unMatchedMeals[indx]]
                        for matchedIndx, matchedMeal in matchedMeals:
                            del unMatchedMeals[matchedIndx]
                            listToAddToMealsToMatch.append(matchedMeal)
                            numUnMatchedMeals -= 1;
                        unMatchedMealsToMatch.append(listToAddToMealsToMatch)
                    # else weren't able to find enough matches for a given meal so take no action and just skip it :/
                    indx += 1


           ###############################
           # This section is just debugging info that could really be deleted
           ################################         
            self.response.write("<h1> To Delete </h1>");
            for todelete in unMatchedMealsToDelete:
                self.response.write("<p> Meal Type : ")
                self.response.write(todelete.mealType)
                self.response.write("   " + dateTimeOjectToString(todelete.startRange) + " - " + dateTimeOjectToString(todelete.endRange) + "     Created: " + dateTimeOjectToString(todelete.created) + "</p>")

            self.response.write("<h1> To Meal </h1>");
            mealNum = 0
            for theMatchedMeals in unMatchedMealsToMatch:
                for theMatchedMeal in theMatchedMeals:
                    self.response.write("<p>")
                    self.response.write(mealNum)
                    self.response.write(" Meal Type : ")
                    self.response.write(theMatchedMeal.mealType)
                    self.response.write("   " + dateTimeOjectToString(theMatchedMeal.startRange) + " - " + dateTimeOjectToString(theMatchedMeal.endRange) + "     Created: " + dateTimeOjectToString(theMatchedMeal.created) + "</p>")
                    mealNum += 1

            # suc, userOb = User.validateLogIn("***REMOVED***", "***REMOVED***")
            # ummls = UnMatchedMeal.getUpcomingUnMatchedMealsForUser(userOb.key.urlsafe())
            # self.response.write("<h1> Unmatched Meals </h1>")
            # for um in ummls:
            #     self.response.write("<p>")
            #     self.response.write(um.startRange)
            #     self.response.write("</p>")

            # mmls = Meal.getUpcomingMealsForUser(userOb.key.urlsafe())
            # self.response.write("<h1> Matched Meals </h1>")
            # for um in mmls:
            #     self.response.write("<p>")
            #     self.response.write(um.startTime)
            #     self.response.write("</p>")


        #delete the meals that are past and never got matched
        unMatchedMealKeysToDelete = [theMeal.key for theMeal in unMatchedMealsToDelete]
        UnMatchedMeal.removeUnMatchedMeals(unMatchedMealKeysToDelete)

        #for the meals that can be paired... pair them
        for theMatchedMeals in unMatchedMealsToMatch:
            firstMeal, secondMeal = theMatchedMeals
            Meal.createNewMeal(firstMeal, secondMeal)



application = webapp2.WSGIApplication([('/mealmatching', MatchMeals)], debug = False)


