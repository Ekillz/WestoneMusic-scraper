from lxml import html
import requests
import re
import json
from album import Album
from track import Track

class AlbumParserError(LookupError):
    pass


class AlbumParser:
    URL_SEARCH = 'http://www.westonemusic.com/search'
    URL_GET_LIBRARY = 'http://www.westonemusic.com/Handlers/GetLibrary.ashx?objectID='
    URL_GET_ALBUM = 'http://www.westonemusic.com/Handlers/GetAlbum.ashx?albumCode='
    URL_GET_TRACK = 'http://www.westonemusic.com/Handlers/GetTrack.ashx?objectid='

    def __init__(self):
        self.nb_http_request = 0

    def parse(self):
        self.label_ids = self.get_label_ids()
        for label_id in self.label_ids:
            self.album_urls = self.get_album_urls(label_id)
            for album_url in self.album_urls:
                print "[" + album_url.split('=')[-1] + "]"
                yield self.get_album_track_data(album_url)


    def get_label_ids(self):
        page = requests.get(self.URL_SEARCH)
        self.nb_http_request += 1
        tree = html.fromstring(page.content)
        label_urls = tree.xpath(
            '//li[@class="text-capitalize"]/a[contains(@href, "label")]/@href')
        label_urls = list(set(label_urls))
        label_urls = [label.split('/')[2] for label in label_urls]
        return label_urls


    def get_album_urls(self, label_id):
        page = requests.get(self.URL_GET_LIBRARY + label_id)
        self.nb_http_request += 1
        data = json.loads(page.text[1:-2])
        tree = html.fromstring(data['albumsHtml'])
        album_urls = tree.xpath('//div[@class="col-xs-6 col-sm-3 col-md-2 ' \
            + 'results-cover album-col"]/figure/a[contains(@href, "album")]/@href')
        album_urls = [self.URL_GET_ALBUM + album.split('/')[4] for album in album_urls]
        print "[" + re.sub("[^a-zA-Z]", "", album_urls[0]).upper()[-3:] \
            + "][LEN]: " + str(len(album_urls))
        return album_urls


    def get_album_track_data(self, album_url):
        page = requests.get(album_url)
        self.nb_http_request += 1
        data = json.loads(page.text[1:-2])
        album = Album(
            data['albumName'], data['albumDesc'],
            self.treat_composer_publisher(data['albumComposerHtml']),
            data['albumLibraryName'], data['albumLibraryLCCode'],
            data['albumCode']
        )
        album.tracks = self.get_tracks_json(data['tracksJson'], album.cat_no)
        return album


    def treat_composer_publisher(self, names):
        names = names.replace("<p>", "").replace("</p>", "")
        names = names.split(',')
        names_json = []
        for name in names:
            affiliation = re.search("\(([^\)]+)\)", name)
            if affiliation:
                affiliation = affiliation.group() \
                    .strip().replace("(", "").replace(")", "")
            else:
                affiliation = ""
            com_pub = re.sub("\(([^\)]+)\)", "", name).strip()
            name_json = {"name": com_pub, "affiliation": affiliation}
            names_json += [name_json]
        return names_json


    def get_tracks_json(self, data, album_reference):
        data = data.replace(', "edits":({ all_trackedits: [  ] })', "")
        data = json.loads(data[2:-1])
        for x in data['all_tracks']:
            page = requests.get(self.URL_GET_TRACK + x['id'])
            self.nb_http_request += 1
            track_data = json.loads(page.text[1:-1])
            track = Track(
                x['title'], x['trackNumber'],
                album_reference,
                self.treat_composer_publisher(track_data['trackPublisher']),
                self.treat_composer_publisher(track_data['trackComposers']),
                track_data['trackFileName']
            )
            yield track
