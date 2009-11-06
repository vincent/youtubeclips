
import sys, gtk, webbrowser

from browser import getSmartBrowser

class BrowserBox(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        #self.browser = webkit.WebView()
        self.browser = getSmartBrowser('mozembed')
        self.browser.set_size_request(300, 200)
        #self.browser.connect('navigation-requested', self.browser_navigation_requested)

        # Single container, to reparetn from fullscreen
        self.browser_container = gtk.VBox()
        self.add(self.browser_container)
        self.browser_container.add(self.browser)

        btn_box = gtk.HBox()

        btn_prev = gtk.Button('<')
        #btn_prev = gtk.Button(None, gtk.STOCK_GO_FORWARD)
        #btn_prev.set_label('')
        btn_prev.connect('clicked', lambda a1,pos:self.jump_result(pos), -1)
        btn_box.add(btn_prev)

        btn_next = gtk.Button('>')
        #btn_next.set_image(gtk.STOCK_GO_BACK)
        #btn_next.set_label('')
        btn_next.connect('clicked', lambda a1,pos:self.jump_result(pos), +1)
        btn_box.add(btn_next)

        btn_fs = gtk.Button(None, gtk.STOCK_ZOOM_IN)
        btn_fs.set_label('+')
        btn_fs.connect('clicked', self.open_fullscreen)
        btn_box.add(btn_fs)

        btn_search = gtk.Button(None, gtk.STOCK_FIND)
        btn_search.set_label('YouTube')
        btn_search.connect('clicked', self.open_search_url)
        btn_box.add(btn_search)

        self.add(btn_box)
        self.show_all()


    def set_fullscreen_callback(self, on_fs_func, off_fs_func):
        self.on_fullscreen = on_fs_func
        self.off_fullscreen = off_fs_func

    def set_page(self, page):
        self.page = page
        self.browser.set_page(self.page)
        self.video_results = None
        self.current_url = None

    def jump_result(self, relpos):
        try:
            #sys.stderr.write('Going to play #' + str(self.current_search_result_pos + relpos) + ' url, out of ' + str(len(self.search_results))+"\n")
            video = self.search_results[self.current_search_result_pos + relpos]
            self.current_search_result_pos += relpos
            self.current_url = video['video_url']
            self.browser.open_url(self.current_url)
            #sys.stdout.write(self.current_url + ' openned'+"\n")
        except:
            pass

    def set_video_results(self, video_results):
        self.page = None
        self.search_results = video_results
        self.current_search_result_pos = 0
        self.jump_result(0)

    def set_search_url(self, search_url):
        self.search_url = search_url

    def handle_clicks(self, widget, event, browser, video_url, search_url):
        pass

    def open_search_url(self, widget):
        webbrowser.open(self.search_url)

    def open_fullscreen(self, widget):

        if self.on_fullscreen:
            self.on_fullscreen()

        # Create a fullscreen window with a browser
        fs_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        fs_window.set_screen(self.get_screen())
        fs_window.set_border_width(2)
        fs_window.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(0,0,0))

        #browser = webkit.WebView()
        #browser = self.browser

        if self.page is not None:
            self.browser.set_page(self.page)
        elif self.current_url is not None:
            self.browser.open_url(self.current_url)

        #fs_window.add(browser)

        fs_window.connect("delete_event", self.delete_event)
        fs_window.connect("key_press_event", self.escape_key_press)

        fs_window.show_all()
        self.browser.reparent(fs_window)
        fs_window.fullscreen()

    def delete_event(self, widget, event, data=None):
        return False

    def escape_key_press(self, widget, event, data=None):
        if event.keyval == gtk.keysyms.Escape:
            if self.off_fullscreen:
                self.off_fullscreen()
            self.browser.reparent(self.browser_container)
            widget.destroy()
        return True

    def browser_navigation_requested(self, widget, frame, net_request):
        #webbrowser.open(net_request.get_uri())
        return False
