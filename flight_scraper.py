DEAL_PAGE = "http://www.theflightdeal.com/category/flight-deals/chicago/"
PHONE_NUMBER_FILE = "numbers.txt"
CONFIG_FILE = "config.txt"


from lxml import html
from googlevoice import Voice
import requests
import sched
import time

'''
Removes non printable characters.
'''
def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i) < 128)

'''
Returns a list of lines, given a filename.
'''
def file_lines(filename):
    file = open(filename, 'r')
    # Remove newline character at the end of each line.
    ls = [x[:-1] for x in file]
    file.close()
    return ls

class FlightScraper:
    '''
    Loads current titles, logs into voice, and starts the main loop.  Sends only
    the most recent deal on startup.
    '''
    def __init__(self):
        '''
        A list of deals, with the most recent trimmed, so that it will be sent
        out on the first iteration.
        '''
        deals = self.getTitles()[1:]
        # Create a set of currentDeals.
        self.currentDeals = {x for x in deals}
        self.voice = Voice()
        try:
            print "Trying to log in from config file: " + CONFIG_FILE
            (username, password) = file_lines(CONFIG_FILE)
            self.voice.login(username, password)
            print "Logged in successfully!"
        except:
            print "Failed to login from config, trying manual login"
            self.voice.login()
            print "Logged in successfully!"
        self.iterations = 0
        self.s = sched.scheduler(time.time, time.sleep)
        self.s.enter(1, 1, self.loop, ())
        self.s.run()

    '''
    Returns a list of deal title names from theflightdeal, with the specific
    page specified in DEAL_PAGE.
    '''
    def getTitles(self):
        try:
            page = requests.get(DEAL_PAGE)
        except:
            print "Failed to load page"
            return []

        tree = html.fromstring(page.content)
        parents = tree.xpath("//h1[@class='post-title']")
        titles = []
        for p in parents:
            titles.append(remove_non_ascii(p.getchildren()[0].text))
        return titles

    '''
    Checks for new flight deals and sends texts if they are found.
    '''
    def update(self):
        titles = self.getTitles()
        newTitles = []
        for t in titles:
            if t not in self.currentDeals:
                newTitles.append(t)
                self.sendText(t)
            else:
                break
        self.currentDeals = {x for x in titles}

    '''
    Sends a msg to each number in numbers.txt.  Used by update function for
    sending texts.
    '''
    def sendText(self, msg):
        print
        print "NEW FLIGHT DEAL"
        print msg
        numberList = file_lines(PHONE_NUMBER_FILE)
        for num in numberList:
            try:
                self.voice.send_sms(num, msg)
                print "- Sent text to " + num
            except:
                print "! Failed to send text to " + num
        print

    '''
    Main loop.  Runs every 5 minutes and checks for new deals by calling update.
    '''
    def loop(self):
        print "Updating deals, currently on iteration: " + str(self.iterations)
        self.iterations += 1
        self.update()
        self.s.enter(300, 1, self.loop, ())

FS = FlightScraper()
