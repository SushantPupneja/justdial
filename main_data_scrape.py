import sys
sys.path.append('beautifulsoup4-4.2.1')
from bs4 import BeautifulSoup
import urllib2
import time
import traceback
# from google.appengine.api import urlfetch

def parsePage(city="Gurgaon", entity="Gym", page_no = 1):
    
    url = "http://www.justdial.com/"+ city+"/"+ entity+"/page-"+str(page_no)
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    req = urllib2.Request(url, headers=hdr)    
    try:
        print url
        page = urllib2.urlopen(req, timeout = 20)
        # urlfetch.set_default_fetch_deadline(20)
    except Exception as exp:
        print "Exception in justSpider, urllib2",str(exp)#, traceback.format_exc()
        raise exp
    
    src = BeautifulSoup(page.read())
    sections = src.find_all("section") #contains all section tags.
    jrcls = [] #each section with jbbg class contains item/gym infromation.
    
    try:
        for e in sections:
            if e.get('class') is not None:
                if "rslwrp" in e['class']:
                    jrcls.append(e)
    except Exception as exp:
        print str(exp), traceback.format_exc()
        raise exp
    print jrcls
    if len(jrcls) == 0: #No more gyms
        return None

    gym_list = []
    for e in jrcls:
        try:
            
            p = e.find_all('p') # first 3 paragraphs contain relevent information.

            gym_num = None
            gym_add = None
            gym_name = None

            for para in p:

                if para['class'][0].strip() == "jcnwrp":

                    spans = para.find_all('span')
                    for span in spans:

                        if span['class'][0].strip() == "jcn":

                            gym_name = span.a["title"]
                            gym_url = span.a["href"].split('/')[-1]

                elif para['class'][0].strip() == "jrcw":
                    gym_num = para.text.strip()

                elif para['class'][0].strip() == "jaid":

                    spans = para.find_all('span')
                    for span in spans:

                        if span['class'][0].strip() == "jaddt":

                            spans2 = span.find_all('span')
                            for span2 in spans2:
                                if span2['class'][0].strip() == "mrehover":
                                     gym_add = span2.text.strip()

            if gym_name is None:
                raise Exception("Assertion Failed. Gym must have a name")

            if gym_add is None:
                print "$$$$\nIgnoring address-less gyms:", gym_name
                continue
            
            """A mini algorithm for removing " in place ,city_name" suffix attached with each gym name"""
            namelen = len(gym_name)
            cut = namelen
            for i in xrange(namelen-3):
                state = 0
                if state == 0 and gym_name[i] == ' ':
                    state = 1
                if state == 1 and gym_name[i+1] == 'i':
                    state = 2
                if state == 2 and gym_name[i+2] == 'n':
                    state = 3
                if state == 3 and gym_name[i+3] == ' ':
                    state = 4
                if state == 4:
                    cut = i
                    break
            gym_name = gym_name[:cut]
            """ algorithm complete"""
            
            gym_list.append((gym_name, gym_num, gym_add, gym_url))

        except Exception as exp:
            print str(exp), traceback.format_exc()
            raise exp

    print "Done page: "+str(page_no)
    return gym_list


parsePage()
