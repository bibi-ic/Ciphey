"""
 ██████╗██╗██████╗ ██╗  ██╗███████╗██╗   ██╗
██╔════╝██║██╔══██╗██║  ██║██╔════╝╚██╗ ██╔╝
██║     ██║██████╔╝███████║█████╗   ╚████╔╝ 
██║     ██║██╔═══╝ ██╔══██║██╔══╝    ╚██╔╝  
╚██████╗██║██║     ██║  ██║███████╗   ██║ 
© Brandon Skerritt
Github: brandonskerritt

Class to determine whether somethine is English or not.
1. Calculate the Chi Squared score of a sentence
2. If the score is significantly lower than the average score, it _might_ be English
    2.1. If the score _might_ be English, then take the text and compare it to the sorted dictionary
    in O(n log n) time.
    It creates a percentage of "How much of this text is in the dictionary?"
    The dictionary contains:
        * 20,000 most common US words
        * 10,000 most common UK words (there's no repition between the two)
        * The top 10,000 passwords
    If the word "Looks like" English (chi-squared) and if it contains English words, we can conclude it is
    very likely English. The alternative is doing the dictionary thing but with an entire 479k word dictionary (slower)
    2.2. If the score is not English, but we haven't tested enough to create an average, then test it against the dictionary

Things to optimise:
* We only run the dictionary if it's 20% smaller than the average for chi squared
* We consider it "English" if 45% of the text matches the dictionary
* We run the dictionary if there is less than 10 total chisquared tests

"""
from scipy.stats import chisquare
from collections import OrderedDict
from string import punctuation
import mathsHelper
"""
    {"E": 12.02, "T": 9.10, "A": 8.12, "O": 7.68, "I": 7.31, "N": 6.95, "S": 6.28, "R": 6.02,
    "H": 5.92, "D": 4.32, "L": 3.98, "U": 2.88, "C": 2.71, "M": 2.61, "F": 2.30, "Y": 2.11,
    "W": 2.09, "G": 2.03, "P": 1.82, "B": 1.49, "V": 1.11, "K": 0.69, "X": 0.17, "Q": 0.11,
    "J": 0.10, "Z": 0.07 
    }
"""
class languageChecker:
    def __init__(self):
        self.languages = {
            "English":
            [0.0855, 0.0160, 0.0316, 0.0387, 0.1210,0.0218, 0.0209, 0.0496, 0.0733, 0.0022,0.0081, 0.0421, 0.0253, 0.0717, 0.0747,0.0207, 0.0010, 0.0633, 0.0673, 0.0894,0.0268, 0.0106, 0.0183, 0.0019, 0.0172,0.0011]
            #{'A': 8.12, 'B': 1.49, 'C': 2.71, 'D': 4.32, 'E': 12.02, 'F': 2.3, 'G': 2.03, 'H': 5.92, 'I': 7.31, 'J': 0.1, 'K': 0.69, 'L': 3.98, 'M': 2.61, 'N': 6.95, 'O': 7.68, 'P': 1.82, 'Q': 0.11, 'R': 6.02, 'S': 6.28, 'T': 9.1, 'U': 2.88, 'V': 1.11, 'W': 2.09, 'X': 0.17, 'Y': 2.11, 'Z': 0.07}
        }
        self.average = 0.0
        self.totalDone = 0.0
        self.oldAverage = 0.0
        self.mh = mathsHelper.mathsHelper()
        self.totalWordsTried = 0.0
    def chiSquared(self, text):
        print(text)
        # creates letter frequency of the text
        # do this so it matches up with the list
        letterFreq = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0}
        for letter in text:
            if letter in letterFreq:
                letterFreq[letter] +=1
            else:
                # if letter is not puncuation, but it is still ascii
                # it's probably a different language so add it to the dict
                if letter not in punctuation and self.isAscii(letter) :
                    letterFreq[letter] = 1
                
        # so we dont have to calculate len more than once
        # turns them into probabilities (frequency distribution)
        lenOfString = len(text)
        for key, value in letterFreq.items():
            try:
                letterFreq[key] = value / lenOfString
            except ZeroDivisionError as e:
                print("Error, you have entered an empty string :( The error is \"" + str(e) +"\" on line 34 of LanguageChecker.py (function chiSquared)")
                exit(1)

        # calculates chi squared of each language
        maxChiSquare = 0.00
        languagesChi = {}
        highestLanguage = ""
        for language in self.languages:
            #, list(languages[language].values())
            temp = self.myChi(letterFreq, self.languages[language])
            languagesChi[language] = temp
            """if temp >= maxChiSquare:
                #maxChiSquare = temp
                highestLanguage = language"""
        # calculates running average
        self.oldAverage = self.average
        self.totalDone += 1
        self.average = self.average + (chisquare / self.totalDone)
        return(languagesChi)
    def sortDictionary(self, dictionary):
        return dict(OrderedDict(sorted(dictionary.items())))
    def myChi(self, text, distribution):
        # chrome-extension://oemmndcbldboiebfnladdacbdfmadadm/https://cgi.csc.liv.ac.uk/~john/comp105resources/lecture10.pdf
        # http://practicalcryptography.com/cryptanalysis/text-characterisation/chi-squared-statistic/
        # given a text frequency and a distribution, calculate it's Chi score
        chiScore = 0.0
        for counter, letter in enumerate(text.values()):
            chiScore = chiScore + ((letter - distribution[counter])**2) / distribution[counter]
        return chiScore
    def isAscii(self, letter):
        # checks if a charecter is ascii
        # https://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
        return bool(lambda s: len(s) == len(s.encode()))
    def checkChi(self):
        # TODO 20% isn't optimal
        # runs after every chi squared to see if it's 1 significantly lower than averae
        # the or statement is bc if the program has just started I don't want it to ignore the 
        # ones at the start
        # TODO is 10 optimal?
        # TODO is 45 optimal?
        if self.mh.percentage(self.oldAverage, self.average) >= 20 or self.totalDone < 10:
            percetageOfEnglish = checkEnglish(text)
            print("Ok, it's significant!")
            if percetageOfEnglish > 45:
                print("I'm pretty sure this is English")
    def checkEnglish(self, text):
        # reads through most common words / passwords
        # and calculates how much of that is in English
        text = text.split(" ")
        text = text.sort()
        f = open("dictionary.txt", "r")
        f = f.readlines()
        counter = 0.00
        # dictionary is "word\n" so I remove the "\n"
        for word[0:-2] in f:
            if word == text:
                counter = counter + 1
        counter = mh.percentage(counter, len(text))
        return counter