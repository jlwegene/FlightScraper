from lxml import html
from googlevoice import Voice
import requests
import sched
import time


class FlightScraper:
    def __init__(self):
        self.currentDeals = self.getTitles()
        self.voice = Voice()
        self.voice.login()
        self.iterations = 0
        self.s = sched.scheduler(time.time, time.sleep)
        self.s.enter(1, 1, self.loop, ())
        self.s.run()

    def getTitles(self):
        try:
            page = requests.get('http://www.theflightdeal.com/category/flight-\
            deals/chicago/')
        except:
            print "Failed to load page"
            return []

        tree = html.fromstring(page.content)
        parents = tree.xpath("//h1[@class='post-title']")
        titles = []
        for p in parents:
            titles.append(self.remove_non_ascii(p.getchildren()[0].text))
        return titles

    def remove_non_ascii(self, text):
        return ''.join(i for i in text if ord(i) < 128)

    def update(self):
        titles = self.getTitles()
        newTitles = []
        for t in titles:
            if t not in self.currentDeals:
                newTitles.append(t)
                print t
                self.sendText(t)
            else:
                break

        self.currentDeals = newTitles + self.currentDeals

    def sendText(self, msg):
        numberFile = open('numbers', 'r')
        for num in numberFile:
            try:
                self.voice.send_sms(num, msg)
            except:
                print "Failed to send text " + msg
                print "Failed number was " + num
        numberFile.close()

    def loop(self):
        print "Updating deals, currently on iteration: " + str(self.iterations)
        self.iterations += 1
        self.update()
        self.s.enter(300, 1, self.loop, ())

FS = FlightScraper()
