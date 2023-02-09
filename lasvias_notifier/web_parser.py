"""Submodule containing the parser for the movie session page."""

import asyncio
import logging
from html.parser import HTMLParser

import requests

from lasvias_notifier.notifier import telegram_notify


class LasViasHTMLParser(HTMLParser):
    """Main page HTML parser."""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__class__.__name__)
        self.content_found = False
        self.prev_images = set()
        self.images = set()

    def handle_starttag(self, tag, attrs):
        if tag == "html":
            self.prev_images = self.images
            self.images = set()

        if self.content_found:
            if tag != "img":
                return
            
            for attr_name, attr_value in attrs:
                if attr_name == "src":
                    self.images.add(attr_value)
                    self.content_found = False
                    return
            
            return

        elif self.content_found:
            return
        
        if tag == "div":
            for attr_name, attr_value in attrs:
                if attr_name != "class":
                    continue

                if "portfolio-item" in attr_value:
                    self.content_found = True

    def get_new_images(self) -> set:
        """Return the list of new images not present in the previous execution."""
        return self.images - self.prev_images


class LasViasFilmsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__class__.__name__)
        self.found_modal_header = False
        self.found_film_title = False
        self.titles = set()
        self.prev_titles = None
    
    def feed(self, text: str) -> None:
        self.prev_titles = self.titles
        super().feed(text)

    def handle_starttag(self, tag, attrs):
        if self.found_modal_header:
            self.handle_starttag_inside_modal_header(tag, attrs)
            return
        
        if tag != "div":
            return

        for attr_key, attr_value in attrs:
            if attr_key == "class" and attr_value == "modal-header":
                self.found_modal_header = True
                return
    
    def handle_endtag(self, tag):
        if self.found_modal_header and tag == "div":
            self.found_modal_header = False

        if self.found_film_title and tag == "h5":
            self.found_film_title = False

    def handle_starttag_inside_modal_header(self, tag, attrs):
        if tag != "h5":
            return

        for attr_key, attr_value in attrs:
            if attr_key == "class" and attr_value == "modal-title":
                self.found_film_title = True

    def handle_data(self, data):
        if not self.found_film_title:
            return
        
        self.titles.add(data.capitalize())


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
