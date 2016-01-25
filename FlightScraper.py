from lxml import html
from googlevoice import Voice
import requests
import sched
import time


class FlightScraper:
    def __init__(self):
        self.currentDeals = []
        self.voice = Voice()
        self.voice.login()
        self.numbers = ['8123455508', '5073180082']
        self.s = sched.scheduler(time.time, time.sleep)
        self.s.enter(1, 1, self.loop, ())
        self.s.run()

    def getTitles(self):
        page = requests.get('http://www.theflightdeal.com/category/flight-deals\
        /chicago/')
        tree = html.fromstring(page.content)
        parents = tree.xpath("//h1[@class='post-title']")
        titles = []
        for p in parents:
            titles.append(self.remove_non_ascii(p.getchildren()[0].text))
        return titles

    def remove_non_ascii(self, text):
        return ''.join(i for i in text if ord(i) < 128)
        # return text.decode('unicode_escape').encode('ascii', 'ignore')

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
        for num in self.numbers:
            try:
                self.voice.send_sms(num, msg)
            except:
                print "Failed to send text " + msg

    def loop(self):
        print "Updating deals. . ."
        self.update()
        self.s.enter(300, 1, self.loop, ())

FS = FlightScraper()
