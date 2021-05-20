'''
NBA Score Alert Window

Version: 1.0
Author: Brian Walheim

Description: Tracks NBA scores and creates an alert for close games
    These alerts can be clicked on to pull up live stream of the game

API Reference:

https://github.com/kashav/nba.js/blob/master/docs/api/DATA.md 
http://data.nba.net/ 
- holds nba score board data 
'''

# Imports

#Handles acccesing of website
import requests
import json

#Imports operating system
import os 

#Handles window creation
from tkinter import *
from win32api import GetSystemMetrics
from PIL import ImageTk, Image

#Handles open the streams
import webbrowser

#Handles time functions
from datetime import datetime
from datetime import timedelta
import time
import pytz

#Handles playing arudio
from playsound import playsound


# Local Variables

#Dictionary that maps
tricodeToName = {
    'ATL':'Atlanta Hawks',
    'BOS':'Boston Celtics',
    'BKN':'Brooklyn Nets',
    'CHA':'Charlotte Hornets',
    'CHI':'Chicago Bulls',
    'CLE':'Cleveland Cavaliers',
    'DAL':'Dallas Mavericks',
    'DEN':'Denver Nuggets',
    'DET':'Detroit Pistons',
    'GSW':'Golden State Warriors',
    'HOU':'Houston Rockets',
    'IND':'Indiana Pacers',
    'LAC':'Los Angeles Clippers',
    'LAL':'Los Angeles Lakers',
    'MEM':'Memphis Grizzlies',
    'MIA':'Miami Heat',
    'MIL':'Milwaukee Bucks',
    'MIN':'Minnesota Timberwolves',
    'NOP':'New Orleans Pelicans',
    'NYK':'New York Knicks',
    'OKC':'Oklahoma City Thunder',
    'ORL':'Orlando Magic',
    'PHI':'Philadelphia 76ers',
    'PHX':'Phoenix Suns',
    'POR':'Portland Trail Blazers',
    'SAC':'Sacramento Kings',
    'SAS':'San Antonio Spurs',
    'TOR':'Toronto Raptors',
    'UTA':'Utah Jazz',
    'WAS':'Washington Wizards'
}

notifiedGames = []
tighterGames = []
OTGames = []

# Notification Interface

class ScoreNotification:

    #Constructs a new notification
    def __init__(self, title="Title", message="message", time="", score1="", score2="", image1="", image2= "",link=""):
        self.title = title
        self.message = message    
        self.imagePath1 = image1
        self.imagePath2 = image2
        self.score1 = score1
        self.score2 = score2
        self.time = time    
        self.link = link

    def notify(self, time):

        #cConfigures screen orientation
        screenWidth = GetSystemMetrics(0)
        screenHeight = GetSystemMetrics(1)

        x=screenWidth-320
        y=screenHeight-200

        windowWidth = 300
        windowHeight = 100 

        #Configures window
        self.window = Tk()
        self.window.geometry(str(windowWidth) + 'x' + str(windowHeight) + '+' + str(x) + '+' + str(y))
        self.window.overrideredirect(True)
        self.window.after(10000, self.destroyWindow)
        self.window.bind("<1>", self.openLink)


        #Loads Team Images
        self.imageFile1 = Image.open(self.imagePath1).resize((75, 75), Image.ANTIALIAS)
        self.image1 = ImageTk.PhotoImage(self.imageFile1)
        self.imageLabel1 = Label(image=self.image1)
        self.imageLabel1.image = self.image1
        self.imageLabel1.place(x=10, y=25)

        self.imageFile2 = Image.open(self.imagePath2).resize((75, 75), Image.ANTIALIAS)
        self.image2 = ImageTk.PhotoImage(self.imageFile2)
        self.imageLabel2 = Label(image=self.image2)
        self.imageLabel2.image = self.image2
        self.imageLabel2.place(x=210, y=25)

        #Configures title text
        self.titleLabel = Label(self.window, text=self.title, font= ("Verdana", 13))
        self.titleLabel.pack()

        #Configures score txt
        self.scoreLabel = Label(self.window, text= self.score1+ "   @   "+self.score2, font=("Verdana",15))
        self.scoreLabel.pack()

        #Configures time label
        self.timeLabel = Label(self.window, text=self.time, font=("Verdana", 8))
        self.timeLabel.pack()

        #Configures message
        self.messageLabel = Label(self.window, text = self.message, font=("Verdana", 9))
        self.messageLabel.pack()

        #Plays alert notification
        playsound('alert.wav')

        #Creates window
        self.window.mainloop()

    #Opens webpage on click of notification
    def openLink(self, event):
        webbrowser.open_new(self.link)
        self.window.destroy()

    #Destroys the window
    def destroyWindow(self):
        self.window.destroy()

    
# Functions

def getCurrentNBAGames(notifiedGames, tighterGames, OTGames):

    #Getting the proper data
    #If connection fails just exits function to prevent error
    try:
        page = requests.get("http://data.nba.net/data/10s/prod/v1/" + getNBADayString() +"/scoreboard.json")
        data = page.json()
    except:
        return None

    #For debugging outputs the json file
    #print(json.dumps(data, indent=2))

    #Flag to see if there are no active games
    activeGames = False

    #Iterates through every game for the day
    for game in data["games"]:

        gameID = game["gameId"]

        homeTeamCode = game["hTeam"]["triCode"]
        homeTeamScore =  game["hTeam"]["score"]

        visitTeamCode = game["vTeam"]["triCode"]
        visitTeamScore = game["vTeam"]["score"]

        gamePeriod = game["period"]["current"]
        timeInPeriod = game["clock"]

        #Checks to see if game is active
        if (homeTeamScore != "" and visitTeamScore != ""):
            activeGames = True
            print("Q" + str(gamePeriod) + " " + timeInPeriod + ": " + visitTeamCode + "(" + visitTeamScore + ")"  + " @ " +  homeTeamCode + "(" + homeTeamScore + ")")
            timeString = "Q" + str(gamePeriod) + " " + timeInPeriod 
            
            #Calculates if the game is close
            if (isCloseGame(int(visitTeamScore), int(homeTeamScore), timeInPeriod, gamePeriod)==1):
                
                #Checks to make sure that we have not been notified for game
                if (gameID not in notifiedGames):

                    #Add game to list of notified game
                    notifiedGames.append(gameID)

                    #Notifies the user about the game
                    notification = ScoreNotification(
                        title="CLOSE GAME ALERT", 
                        message= visitTeamCode + " vs " + homeTeamCode, 
                        score1 = homeTeamScore,
                        score2 = visitTeamScore,
                        time = timeString,
                        image1=getPathToImages(visitTeamCode),
                        image2=getPathToImages(homeTeamCode),
                        link=getStreamLink(homeTeamCode, visitTeamCode))
                    notification.notify(10)

            elif(isCloseGame(int(visitTeamScore), int(homeTeamScore), timeInPeriod, gamePeriod)==2):
                #Checks to make sure that we have not been notified for game
                if (gameID not in tighterGames):

                    #Add game to list of notified game
                    tighterGames.append(gameID)

                    #Notifies the user about the game
                    notification = ScoreNotification(
                        title="CLOSER GAME ALERT", 
                        message= visitTeamCode + " vs " + homeTeamCode, 
                        score1 = homeTeamScore,
                        score2 = visitTeamScore,
                        time = timeString,
                        image1=getPathToImages(visitTeamCode),
                        image2=getPathToImages(homeTeamCode),
                        link=getStreamLink(homeTeamCode, visitTeamCode))
                    notification.notify(10)

            elif(isCloseGame(int(visitTeamScore), int(homeTeamScore), timeInPeriod, gamePeriod)==3):
                #Checks to make sure that we have not been notified for game
                if (gameID not in OTGames):

                    #Add game to list of notified game
                    OTGames.append(gameID)

                    #Notifies the user about the game
                    notification = ScoreNotification(
                        title="OT GAME ALERT", 
                        message= visitTeamCode + " vs " + homeTeamCode, 
                        score1 = homeTeamScore,
                        score2 = visitTeamScore,
                        time = timeString,
                        image1=getPathToImages(visitTeamCode),
                        image2=getPathToImages(homeTeamCode),
                        link=getStreamLink(homeTeamCode, visitTeamCode))
                    notification.notify(10)

    #If games are over clears notified games
    if(not activeGames):
        notifiedGames = []
        tighterGames = []
        OTGames = []

        #Sleeps for 2 hours
        time.sleep(7200)
        

#Generates path to images taking the team tricode
def getPathToImages(teamTriCode):
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    pathToImageDirectory = dir_path + "\\TeamLogos\\"
    teamName = tricodeToName[teamTriCode].lower().replace(" ","-")
    return pathToImageDirectory + teamName + ".png"


#Returns formatted string for the current NBA dayString
#   NBA day is defined as day of NBA games
#   Returns: String formatted YYYYMMDD
def getNBADayString():

    tz_NY = pytz.timezone('America/New_York') 
    datetime_NY = datetime.now(tz_NY)
    if(int(datetime_NY.strftime("%H")) <= 3):
        datetime_NY = datetime_NY - timedelta(1)
        return datetime_NY.strftime("%Y%m%d")

    return datetime_NY.strftime("%Y%m%d")


#Takes in the hTeam and vTeam tricodes and generates
# the link to the stream    
def getStreamLink(hTeamCode, vTeamCode):

    #home team and the visiting team
    #http://liveonscore.tv/nba-stream/home-team-vs-away-team/
    homeTeam = tricodeToName[hTeamCode].lower().replace(" ","-")
    awayTeam = tricodeToName[vTeamCode].lower().replace(" ","-")
    return "http://liveonscore.tv/nba-stream/"+homeTeam+"-vs-"+awayTeam+"/"


#Returns int if team is clsoe
#   Close game is defined as withing 5 minutes
#   and score diferential of 5 or less
#
#   Input: both team scores
#          time left in the quarter
#          period is quarter of the game
#
#   Returns: 0 - if not close
#            1 - if close within 5 minutes
#            2 - if close within 2 minutes
#            3 - if close within overtime
def isCloseGame(score1, score2, time, period):

    scoreDifferential = abs(score1-score2)

    minutes = 0
    if(":" in time):
        minutes = int(time.split(":")[0])

    #Checks for close game within OT
    if(scoreDifferential <= 5 and period > 4):
        return 3

    #Checks for the close game within 2 minutes
    if(scoreDifferential <= 5 and period == 4 and (":" not in time or minutes<2) and time != ""):
        return 2

    #Checks for theclose game within 5 minutes
    elif(scoreDifferential <= 5 and period == 4 and (":" not in time or minutes<5) and time != ""):
        return 1
    
    #Returns 0 if not close
    return 0


# Main


#Main loop checks scores every 15 seconds
while True:
    getCurrentNBAGames(notifiedGames, tighterGames, OTGames)
    time.sleep(15)


'''
notification = ScoreNotification(
    title="CLOSE GAME ALERT", 
    message= "LAL" + " vs " + "PHI", 
    score1 = str(0),
    score2 = str(0),
    time = "1:30",
    image1= getPathToImages("MEM"),
    image2= getPathToImages("PHI"),
    link="www.google.com")

notification.notify(5)
'''
