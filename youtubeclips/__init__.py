#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rb, sys
import rhythmdb
import gtk.gdk

from youtuberequest import YouTubeRequest
from browserbox import BrowserBox

alternate_engines = {
        'Dailymotion': {
            'url': 'http://www.dailymotion.com/relevance/search/%(artist_name)s %(song_name)s'
        }
}

class YouTubeClipsPlugin (rb.Plugin):

    def log(self, message):
        sys.stderr.write(message + "\n")

    def playing_changed(self, sp, playing):
        if not playing: return False

        # Get artist / song names
        entry = sp.get_playing_entry()
        entry_id = self.rhymthdb.entry_get(entry, rhythmdb.PROP_ENTRY_ID)

        if entry_id == self.current_entry_id: return False
        self.current_entry_id = entry_id

        artist_name = self.rhymthdb.entry_get(entry, rhythmdb.PROP_ARTIST)
        song_name = self.rhymthdb.entry_get(entry, rhythmdb.PROP_TITLE)

        search_params = {
            'artist_name': artist_name,
            'song_name': song_name
        }

        api_params = search_params.copy()
        api_params.update({
            'category': 'Music',
            'vq': artist_name + "+" + song_name,
            'racy': 'include',
            'orderby': 'viewCount'
        })

        # Our search urls
        www_url = "http://www.youtube.com/results?search_query=Music+" + artist_name + "+" + song_name

        #try:
        if True:
            search_results = self.ytsearch.search(api_params)
            self.set_browser_box(www_url, search_results=search_results)
        #except:
        #    self.log("Network is not reachable")
        #    if self.browser_box is not None: self.browser_box.hide()

            #return False

            # No video found
            # show the default page
            self.set_browser_box(www_url, page=self.get_default_page(search_params))


    def set_browser_box(self, search_url, search_results=None, page=None):
        if self.browser_box is None:
            b_box = BrowserBox()
            self.shell.add_widget (b_box, rb.SHELL_UI_LOCATION_SIDEBAR)
            self.browser_box = b_box

            def on_fullscreen():
                self.shell.props.shell_player.pause()

            def off_fullscreen():
                self.shell.props.shell_player.play()

            self.browser_box.set_fullscreen_callback(on_fullscreen, off_fullscreen)

        self.browser_box.set_search_url(search_url)

        if search_results is not None:
            self.browser_box.set_video_results(search_results)

        elif page is not None:
            self.browser_box.set_page(page)

    def get_default_page(self, search_params):
        return """
            <div style="width:100%; height:100%; padding:0; margin:0; ">
                <h1>Oops</h1>
                <p>""" + _("Sorry, I haven't found a video clip for this music.<br/>You can use the following YouTube search button, or") + """</p>
                <ul>
                """ + "\n".join([ ("<li>" + ("<a href=\"%s\">" % engine_config.get('url')) + ("search on %s" % engine_name) + "</a></li>") % search_params for engine_name, engine_config in alternate_engines.iteritems() ]) + """
                </ul>
            </div>
            """

    def activate(self, shell):
        # Keep a self ref on shell db
        self.current_entry_id = None
        self.browser_box = None
        self.rhymthdb = shell.props.db
        self.shell = shell

        self.ytsearch = YouTubeRequest()
        
        self.event_ids = {
            'playing_changed': shell.get_player().connect('playing-changed', self.playing_changed),
        }

    def desactivate(self, shell):
        for id in self.event_ids:
            self.disconnect(id)

        del self.event_ids
        del self.ytsearch
        del self.browser_box
        del self.shell
        del self.rhymthdb


