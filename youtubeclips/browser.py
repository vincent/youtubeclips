
def get_webkit_browser():
    import webkit
    b = webkit.WebView()

    def __set_page(page):
        b.load_html_string(page, '')
    b.set_page = __set_page

    def __open_url(url):
        b.open(url)
    b.open_url = __open_url
    return b

def get_mozembed_browser():
    import gtkmozembed
    b = gtkmozembed.MozEmbed()

    def __set_page(page):
        #b.append_data(page, len(page))
        b.render_data(page, len(page), '', 'text/html')
    b.set_page = __set_page

    def __open_url(url):
        b.load_url(url)
    b.open_url = __open_url
    return b

def getSmartBrowser(forced = None):
    if forced == 'webkit':
        return get_webkit_browser()
    elif forced == 'mozembed':
        return get_mozembed_browser()

    try:
        b = get_webkit_browser()
    except:
        b = get_mozembed_browser()
    return b