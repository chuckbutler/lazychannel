import requests
import logging
import subprocess
import shlex
import os
import unicodedata as ucode
from lazychannel.helpers import pexpand, output_dir


class youtube:
    def __init__(self, cache_file):
        self.log = logging.getLogger('lazychannel.worker.youtube')
        self.BASE_URL = "http://gdata.youtube.com/feeds/api/videos?max-results"
        "=50&alt=json&orderby=published&author={}"
        self.cache_file = cache_file

    def fetch_channel(self, uuid):
        channel_url = self.BASE_URL.format(uuid)
        channel_list = requests.get(channel_url).json()
        return channel_list

    def download(self, uuid, out):
        videos = self.fetch_channel(uuid)
        if 'entry' not in videos['feed']:
            self.log.error('No feed found, assuming account deleted.')
            return
        for v in videos['feed']['entry']:
            link = v['link'][0]['href']
            title = ucode.normalize('NFKD', v['title']['$t'])
            title = title.encode('ascii', 'ignore')
            if not self.in_cache(link):
                self.log.info('Fetching {}'.format(title))
                self.call_downloader(out, link)
            else:
                self.log.debug('Cache Hit on: {} - skipping'.format(title))

    def in_cache(self, link):
        # obnoxious bug
        link = "{}\n".format(link)
        with open(self.cache_file, 'r') as f:
            cache = f.readlines()
        if link in cache:
            return True
        return False

    def call_downloader(self, outpath, link):
        outpath = "{}{}%(title)s.%(ext)s".format(outpath, os.path.sep)
        c = "youtube-dl -x --audio-format=mp3 -o {} {}".format(outpath, link)
        cmd = shlex.split(c)
        subprocess.check_output(cmd)
        with open(self.cache_file, 'a+') as f:
            f.write("{}\n".format(link))

    def main(self, channels, out, ws):
        self.log.info('Initialized youtube processor')
        for chan in channels:
            self.log.info("Processing {}".format(chan))
            out = pexpand(os.path.join(out, chan))
            output_dir(out)
            self.download(channels[chan], out)
