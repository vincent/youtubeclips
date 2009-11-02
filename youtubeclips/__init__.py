#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rb, sys
import rhythmdb
import gtk.gdk

import urllib, urllib2
import xml.etree.ElementTree as ET

import webkit, webbrowser

class YouTubeClipsPlugin (rb.Plugin):

    def log(self, message):
        sys.stderr.write(message + "\n")

    def playing_changed(self, sp, playing):
        if not playing: return False

        # Get artist / song names
        entry = sp.get_playing_entry()
        artist_name = self.rhymthdb.entry_get(entry, rhythmdb.PROP_ARTIST)
        song_name = self.rhymthdb.entry_get(entry, rhythmdb.PROP_TITLE)

        params = urllib.urlencode({
            'category': 'Music',
            'vq': artist_name + "+" + song_name,
            'racy': 'include',
            'orderby': 'viewCount'
        })

        # Our search urls
        api_url = "http://gdata.youtube.com/feeds/api/videos?%s" % params
        www_url = "http://www.youtube.com/result?http://www.youtube.com/results?search_query=Music+" + artist_name + "+" + song_name

        self.log("Using url : %s" % api_url)

        # Get YouTube query results as XML
        """
        loader = rb.Loader()
        loader.get_url(api_url, self.setup_video_from_feed)
        """
        results = urllib2.urlopen(api_url)
        results = results.read()

        # Load an XML ElementTree
        feed = ET.fromstring(results)

        # Pick the first
        videoentry = feed.find('{http://www.w3.org/2005/Atom}entry')

        # Extract video link
        video_url = videoentry.find('{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}content')
        if video_url is not None: video_url = video_url.get('url')

        # 2nd try, use <player>
        if video_url is None:
            video_url = videoentry.find('{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}player')
            if video_url is not None: video_url = video_url.get('url')

        # Get a browser on the video link,
        # with link to search results
        if video_url is None and self.browser is not None:
            self.browser.hide()
            return False

        self.log("Video url found : %s" % video_url)

        self.get_browser(video_url, www_url)

        self.log("Show browser")

    def handle_clicks(self, widget, event, video_url, search_url):
        pass

    def open_fullscreen(self, widget, event, video_url, search_url):
        fs_window = gtk.Window(gtk.TOPLEVEL)
        fs_window.set_border_width(2)
        fs_window.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(0,0,0))
        browser = webkit.WebView()
        browser.set_size_request(300, 200)
        browser.open(video_url)
        fs_window.fullscreen()
        fs_window.add(browser)

        def escape_key_press(widget, event):
            if event.keyval == gtk.keysyms.Escape:
                widget.destroy()

        fs_window.connect("key_press_event", escape_key_press)

        fs_window.show_all()

    def get_browser(self, video_url, search_url):
        if self.browser is None:
            vbox = gtk.VBox()
            browser = webkit.WebView()
            browser.set_size_request(300, 200)
            self.browser = browser
            vbox.add(browser)

            btn_fs = gtk.Button(_('F'))
            btn_fs.connect('button_release_event', self.open_fullscreen, video_url, search_url)
            vbox.add(btn_fs)

            self.shell.add_widget (vbox, rb.SHELL_UI_LOCATION_SIDEBAR)
            vbox.show_all()
        else:
            browser = self.browser
            browser.disconnect(self.browser_menu_eventid)

        self.browser_menu_eventid = browser.connect('button_release_event', self.handle_clicks, video_url, search_url)

        #self.search_url = search_url
        #self.video_url = video_url
        self.log("Open video url")
        browser.open(video_url)
        return browser

    def activate(self, shell):
        # Keep a self ref on shell db
        self.rhymthdb = shell.props.db
        self.shell = shell

        self.event_ids = {
            'playing_changed': shell.get_player().connect('playing-changed', self.playing_changed),
        }

        self.browser = None

    def desactivate(self, shell):
        for id in self.event_ids:
            self.disconnect(id)

        del self.event_ids
        del self.browser
        del self.shell
        del self.rhymthdb


