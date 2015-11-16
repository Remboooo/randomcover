import html
import random
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from urllib.request import urlopen

import re
from bs4 import BeautifulSoup


def get_flickr_image():
    soup = BeautifulSoup(urlopen("https://www.flickr.com/explore/interesting/7days/"), "html.parser")
    containers = soup.find_all('span', class_='photo_container')
    flickr_page = "https://www.flickr.com" + containers[4].find('a')['href']
    soup = BeautifulSoup(urlopen(flickr_page), "html.parser")
    return (flickr_page, soup.find('img', class_='main-photo')['src'])


def get_artist():
    page = urlopen("https://en.wikipedia.org/wiki/Special:Random")
    url = page.geturl()
    soup = BeautifulSoup(page, "html.parser")
    artist = soup.find('h1').text
    return url, re.sub("[\(\[].*?[\)\]]", "", artist)


def get_title():
    quotes = []
    while not quotes:
        page = urlopen("https://en.wikiquote.org/wiki/Special:Random")
        url = page.geturl()
        soup = BeautifulSoup(page, "html.parser")
        div = soup.find('div', id="mw-content-text")
        for ul in div.find_all('ul', recursive=False):
            for li in ul.find_all('li', recursive=False):
                for match in re.findall("([A-Z][A-Za-z'\", ]+[A-Za-z]{2,} [A-Za-z]{2,}[.?!])( |$)", li.text):
                    quote = match[0]
                    if quote[-1] == '.':
                        quote = quote[:-1]
                    quotes.append((url, quote))
    url, title = random.choice(quotes)
    words = title.split(' ')
    title = ' '.join(words[-random.randint(3, 5):])
    return url, title


def generate_album_html():
    with open("template.html", "r") as file:
        template = file.read()

    flickr_page, image = get_flickr_image()
    wikipedia_page, artist = get_artist()
    wikiquote_page, title = get_title()

    return template.format(flickr_page=flickr_page, image=image,
        wikipedia_page=wikipedia_page, artist=html.escape(artist),
        wikiquote_page=wikiquote_page, title=html.escape(title))


class MyRequestHandler(SimpleHTTPRequestHandler):
    def send(self, stuff):
        self.wfile.write(stuff.encode())

    def do_GET(self):
        if self.path == '/':
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.send(generate_album_html())
        elif self.path.endswith('.js') or self.path.endswith('.css'):
            super().do_GET()


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyRequestHandler)
    httpd.serve_forever()
