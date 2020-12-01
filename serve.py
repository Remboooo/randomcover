import logging
import html
import random
import re
import sys
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from urllib.request import urlopen


log = logging.getLogger(__name__)


prune_title_prefixes = set([
    'is', 'and', 'of', 'are', 'then', 'than', 'has', 'had', 'him', 'but', 'that', 'to', 'by', 'us', 'they', 'you', 'me'
])

forbidden_title_endings = set([
    'mr', 'mrs', 'dr', 'ft'
])

prune_artist_prefixes = set([
    'list', 'of'
])

prune_artist_endings = set([
    'is', 'and', 'of', 'are', 'then', 'than', 'has', 'had', 'him', 'but', 'that'
])

max_artist_words = 6


def get_flickr_image():
    soup = BeautifulSoup(urlopen("https://www.flickr.com/explore/interesting/7days/"), "html.parser")
    containers = soup.find_all('span', class_='photo_container')
    flickr_page = "https://www.flickr.com" + containers[4].find('a')['href']
    soup = BeautifulSoup(urlopen(flickr_page), "html.parser")
    return (flickr_page, soup.find('img', class_='main-photo')['src'])


def get_artist():
    for i in range(6):
        page = urlopen("https://en.wikipedia.org/wiki/Special:Random")
        url = page.geturl()
        soup = BeautifulSoup(page, "html.parser")
        artist = soup.find('h1').text
        
        # Cut out parentheses etc
        artist = re.sub("[\(\[].*?[\)\]]", "", artist)

        words = artist.split(' ')

        # Prune non-alphabetic (e.g. numeric) prefixes or things like 'list of'
        while words and (words[0].lower() in prune_artist_prefixes or re.fullmatch(r"[^A-Za-z]+", words[0])):
            words = words[1:]
    
        # Cut to max word count
        words = words[:max_artist_words]

        # Prune disallowed postfixed
        while words and words[-1].lower() in prune_artist_endings:
            words = words[:-1]

        # If nothing left, try again with new random page
        if not words: continue

        artist = ' '.join(words)
        return url, artist
    raise Exception("Could not get artist :(")


def get_title():
    titles = []
    for i in range(3):
        page = urlopen("https://en.wikiquote.org/wiki/Special:Random")
        url = page.geturl()
        soup = BeautifulSoup(page, "html.parser")
        div = soup.find('div', id="mw-content-text")
        for ul in div.find_all('ul', recursive=True):
            for li in ul.find_all('li', recursive=False):
                # Try to match some kind of sentence starting with a capital letter, containing at least 2 words and ending in punctuation
                for match in re.findall("([A-Z][A-Za-z'\", ]+[A-Za-z]{2,} [A-Za-z]{2,}[.?!;])( |$)", li.text):
                    quote = match[0]

                    # Remove unwanted punctuation
                    while quote and quote[-1] in ('.', ';', '?', "'", '"'):
                        quote = quote[:-1]

                    while quote and quote[0] in ('.', ':', '?', "'", '"'):
                        quote = quote[1:]
                    
                    # Split to words and cut to random length
                    words = quote.split(' ')
                    words = words[-random.randint(3, 5):]

                    # Prune unwanted prefix words
                    while words and words[0].lower() in prune_title_prefixes:
                        words = words[1:]
                    if not words: continue

                    # Discard if sentence ends in "Dr" or "Mrs" etc; this is not a real sentence
                    if words[-1].lower() in forbidden_title_endings: continue

                    title = ' '.join(words)
                    titles.append((url, title))
        if titles:
            break
    else:
        raise Exception("no title :(")
    url, title = random.choice(titles)
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
        self.path = self.path.split('/')[-1]
        if self.path.endswith('.js') or self.path.endswith('.css'):
            super().do_GET()
        else:
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.send(generate_album_html())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def main():
    argparse = ArgumentParser(description="Random album cover generator service")
    argparse.add_argument("--port", "-p", nargs="?", type=int, default=8080, help="TCP port to bind to")
    argparse.add_argument("--address", "-a", nargs="?", type=str, default="127.0.0.1", help="Address to bind to")
    argparse.add_argument("--verbose", "-v", action="store_true", help="Verbose mode (debug logging)")
    args = argparse.parse_args()

    logging.basicConfig(format='%(asctime)s [ %(levelname)5s | %(name)s ] %(message)s', level=logging.DEBUG if args.verbose else logging.INFO, stream=sys.stdout)

    log.info(f"Starting HTTP server on {args.address}:{args.port}")
    httpd = ThreadedHTTPServer((args.address, args.port), MyRequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    main()

