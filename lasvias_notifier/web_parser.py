"""Submodule containing the parser for the movie session page."""

from html.parser import HTMLParser

import requests


class SessionHTMLParser(HTMLParser):
    """Session page HTML parser."""
    def __init__(self):
        super().__init__()
        self.content_found = False

    def handle_starttag(self, tag, attrs):
        if tag == "div" and ("class", "container margin") in attrs:
            self.content_found = True

    def handle_data(self, data):
        if not self.content_found:
            return
        
        print(data)

    def handle_endtag(self, tag):
        if not self.content_found:
            return
        
        print(tag)
        self.content_found = False


def check_available(base_url, minimal_index) -> str:
    """Check if a new session was posted in the web."""

    url = f"{base_url}/{minimal_index+1}/menudamierdalasvias"
    response = requests.get(url)
    # parser = SessionHTMLParser()
    # parser.feed(response.text)
    # breakpoint()

    if "A PHP Error was encountered" in response.text:
        return ""
    
    else:
        return url
