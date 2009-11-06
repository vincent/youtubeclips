
import sys
import urllib, urllib2
import xml.etree.ElementTree as ET


class YouTubeRequest():

    def __init__(self):
        self.searchs = {}

    def search(self, api_params):

        # Our api URL
        api_url = "http://gdata.youtube.com/feeds/api/videos?%s" % urllib.urlencode(api_params)

        # Offline testing api URL
        #api_url = "file:///home/vincent/workspace/rhythmbox_youtubeclips/youtubeclips/example_results.xml"

        if self.searchs.has_key(api_url):
            ret = self.searchs[api_url]

        else:

            # Get YouTube query results as XML
            results = urllib2.urlopen(api_url)

            results = results.read()

            # Load an XML ElementTree
            feed = ET.fromstring(results)

            # Pick up entries
            videoentries = feed.findall('{http://www.w3.org/2005/Atom}entry')

            if videoentries is None:
                ret = False
            else:
                ret = [ self.extract_entry_details(entry) for entry in videoentries ]

            self.searchs[api_url] = ret

        return ret

    def extract_entry_details(self, result):
        details = {}

        # Extract video title
        video_title = result.findtext('{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}title')

        # Extract video link
        video_url = result.find('{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}content')
        if video_url is not None: video_url = video_url.get('url')

        # 2nd try, use <player>
        if video_url is None:
            video_url = result.find('{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}player')
            if video_url is not None: video_url = video_url.get('url')

        details['video_title'] = video_title
        details['video_url'] = video_url

        return details

