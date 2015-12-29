"""
This file contains miscellaneous functions used throughout the APIs and classes
"""

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