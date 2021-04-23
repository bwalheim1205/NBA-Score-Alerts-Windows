#Handles acccesing of website
import requests
import json

import os 

#Handles window creation
from tkinter import *
from win32api import GetSystemMetrics
from PIL import ImageTk, Image

import webbrowser

from datetime import datetime
from datetime import timedelta
import time
import pytz

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

        #Creates window
        self.window.mainloop()

    #Opens webpage on click of notification
    def openLink(self, event):
        webbrowser.open_new(self.link)
        self.window.destroy()

    #Destroys the window
    def destroyWindow(self):
        self.window.destroy()

    

def getCurrentNBAGames():

    #getting the proper data
    page = requests.get("http://data.nba.net/data/10s/prod/v1/" + getNBADayString() +"/scoreboard.json")
    data = page.json()

    #print(json.dumps(data, indent=2))

    for game in data["games"]:

        homeTeamCode = game["hTeam"]["triCode"]
        homeTeamScore =  game["hTeam"]["score"]

        visitTeamCode = game["vTeam"]["triCode"]
        visitTeamScore = game["hTeam"]["score"]

        gamePeriod = game["period"]["current"]
        timeInPeriod = game["clock"]

        #print("Q" + str(gamePeriod) + " " + timeInPeriod + ": " + visitTeamCode + "(" + visitTeamScore + ")"  + " @ " +  homeTeamCode + "(" + homeTeamScore + ")")

        if (homeTeamScore != "" and visitTeamScore != ""):
            print("Q" + str(gamePeriod) + " " + timeInPeriod + ": " + visitTeamCode + "(" + visitTeamScore + ")"  + " @ " +  homeTeamCode + "(" + homeTeamScore + ")")
            timeString = "Q" + str(gamePeriod) + " " + timeInPeriod 
            if (isCloseGame(int(visitTeamScore), int(homeTeamScore), timeInPeriod, gamePeriod)):
                
                notification = ScoreNotification(
                    title="CLOSE GAME ALERT", 
                    message= visitTeamCode + " vs " + homeTeamCode, 
                    score1 = homeTeamScore,
                    score2 = visitTeamScore,
                    time = timeString,
                    image1=getPathToImages(visitTeamCode),
                    image2=getPathToImages(homeTeamCode),
                    link=getStreamLink(homeTeamCode, visitTeamCode))
                notification.notify(5)


def getPathToImages(teamTriCode):
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    pathToImageDirectory = dir_path + "/TeamLogos/"
    teamName = tricodeToName[teamTriCode].lower().replace(" ","-")
    return pathToImageDirectory + teamName + ".png"

def getNBADayString():

    tz_NY = pytz.timezone('America/New_York') 
    datetime_NY = datetime.now(tz_NY)
    if(int(datetime_NY.strftime("%H")) <= 3):
        datetime_NY = datetime_NY - timedelta(1)
        return datetime_NY.strftime("%Y%m%d")

    return datetime_NY.strftime("%Y%m%d")


    
def getStreamLink(hTeamCode, vTeamCode):

    #home team and the visiting team
    #http://liveonscore.tv/nba-stream/home-team-vs-away-team/
    homeTeam = tricodeToName[hTeamCode].lower().replace(" ","-")
    awayTeam = tricodeToName[vTeamCode].lower().replace(" ","-")
    return "http://liveonscore.tv/nba-stream/"+homeTeam+"-vs-"+awayTeam+"/"

def isCloseGame(score1, score2, time, period):

    scoreDifferential = abs(score1-score2)

    minutes = 0
    if(":" in time):
        minutes = int(time.split(":")[0])

    if(scoreDifferential <= 5 and period == 4 and (":" not in time or minutes<=5) and time != ""):
        return True

    return False



'''
while True:
    getCurrentNBAGames()
    time.sleep(15)
'''


notification = ScoreNotification(
    title="CLOSE GAME ALERT", 
    message= "LAL" + " vs " + "PHI", 
    score1 = str(0),
    score2 = str(0),
    time = "1:30",
    image1= getPathToImages("LAL"),
    image2= getPathToImages("PHI"),
    link="www.google.com")

notification.notify(5)
