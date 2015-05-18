import soundcloud
import requests
from id3parse import ID3, ID3TextFrame, ID3CommentFrame
import os
import pickle
from urllib.parse import *
import sys

class soundcloud_archive:

    def __init__(self):
        print(os.environ.get('SC_CLIENT'),os.environ.get('SC_SECRET'))
        self.client = soundcloud.Client(
            client_id=os.environ.get('SC_CLIENT'),
            client_secret=os.environ.get('SC_SECRET'),
            redirect_uri='http://www.decaffeinated.io/projects/sc_code.html',
            scope='non-expiring')

        if os.path.isfile('access.pkl'):
            self.access_token = pickle.load(open('access.pkl', 'rb'))
        else:
            print(self.client.authorize_url())
            code = input('what is your code? >')
            self.access_token = self.client.exchange_token(
                code=code).access_token
            pickle.dump(self.access_token, open('access.pkl', 'wb'))

        self.get_likes()

    def download_set(self, likes):
        for like in likes.collection:
            try:
                self.download_song(like['permalink_url'])
            except requests.exceptions.HTTPError as e:
                print(e,like['permalink_url'])

    def get_next_href(self,href):
        next_likes = self.client.get(href)
        self.download_set(next_likes)
        try:
            next_href = next_likes.next_href
            if parse_qs(urlparse(next_href).query)['page_number'][0] != parse_qs(urlparse(href).query)['page_number'][0] and next_href:
                self.get_next_href(next_href)
        except AttributeError as e:
            print(e)

    def get_likes(self):
        # get user id
        temp_client = soundcloud.Client(access_token=self.access_token)
        me = temp_client.get('/me')
        user_id = me.id
        total_count = me.public_favorites_count
        print('Found %i likes.' % total_count)
        if total_count > 400:
            print('Only able to download first 400 songs - https://twitter.com/soundclouddev/status/564649386517737472 .')
        # get public likes
        likes = self.client.get('/users/%i/favorites' % user_id,limit=200,linked_partitioning=1)
        self.download_set(likes)
        try:
            self.get_next_href(likes.next_href)
        except AttributeError as e:
            print(e)
        print('')

    def get_attributes(self, song):
        title = song.title.replace('/', ' ')
        artist = song.user['username'].replace('/', ' ')
        description = song.description
        tags = ' '.join(['#%s' % x for x in song.tag_list.split(' ')])
        comments = None
        if len(tags) > 1:
            comments = "%s\n%s" % (description, tags)
        else:
            comments = description
        permalink = song.permalink_url
        return {"title": title, "artist": "%s" % artist, "comments": comments, 'publisher': permalink}

    def check_directory(self):
        if os.path.isdir('soundcloud_downloads') == False:
            os.mkdir('soundcloud_downloads')

    def check_file(self, output_filename):
        if os.path.isfile(output_filename):
            return True
        else:
            return False

    def write_id3(self, output_filename, attributes):
        # TT2 = track name
        # TP1 = artist
        # COM = comments
        # TPUB = publisher (permalink)

        id3 = ID3.from_file(output_filename)

        id3.add_frame(ID3TextFrame.from_scratch('TPE1', attributes['artist']))
        id3.add_frame(ID3TextFrame.from_scratch('TIT2', attributes['title']))
        id3.add_frame(
            ID3CommentFrame.from_scratch('en', 'source', attributes['comments']))
        id3.add_frame(
            ID3TextFrame.from_scratch('TPUB', attributes['publisher']))
        id3.to_file()

    def download_song(self, url):
        print('.',end="")
        sys.stdout.flush()
        song = self.client.get('/resolve', url=url)
        url = self.client.get(
            '/tracks/%s/stream' % song.id, allow_redirects=False).location.replace('https', 'http')

        attributes = self.get_attributes(song)

        self.check_directory()

        output_filename = 'soundcloud_downloads/%s - %s.mp3' % (
            attributes['artist'], attributes['title'])

        if self.check_file(output_filename) == False:
            with open(output_filename, 'wb') as output_file:
                output_file.write(requests.get(url).content)
                self.write_id3(output_filename, attributes)

if __name__ == '__main__':
    soundcloud_archive()
