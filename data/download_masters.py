import json
import discogs_client
import os
import sys

from termcolor import cprint
from time import sleep
from unipath import Path


def get_masters_ids():
    masters_file = Path(__file__).parent.child('masters_ids.txt')
    with open(masters_file, 'r') as fd:
        return sorted(set([l.strip() for l in fd.readlines()]))


def get_discogs_client():
    user_token = os.environ.get('DISCOGS_USER_TOKEN')
    if not user_token:
        msg = 'You must set DISCOGS_USER_TOKEN value in your environment variables'
        cprint(msg, 'red')
        return
    return discogs_client.Client('JazzGraph/0.1', user_token=user_token)


def get_main_release_data(discogs, master_id):
    """
    The API has a rate limit of 60 requests per minute, so that's why I'm always
    sleeping 1 second before each new API request.
    """
    try:
        sleep(1)
        master = discogs.master(master_id)
        master.refresh()

        main_release = master.data.get('main_release')
        if not main_release:
            msg = '\tMaster #{} without main release info'.format(master.id)
            cprint(msg, 'white')
            return

        sleep(1)
        release = discogs.release(main_release)
        release.refresh()
        return release.data
    except Exception:
        return


class MasterMainReleasesCache():

    def __init__(self):
        self.output_json_file = Path(__file__).parent.child('master_releases.json')

    def update(self, master_releases):
        with open(self.output_json_file, 'w') as fd:
            json.dump(master_releases, fd)

    def all_data(self):
        with open(self.output_json_file, 'r') as fd:
            return json.load(fd)


if __name__ == '__main__':
    discogs = get_discogs_client()
    if not discogs:
        sys.exit(0)

    cache = MasterMainReleasesCache()
    master_releases = cache.all_data() or {}

    ids = get_masters_ids()
    resp_404 = []
    for i, master_id in enumerate(ids):
        msg = 'Processing master #{} ({} out of {})'.format(master_id, i + 1, len(ids))
        cprint(msg, 'yellow')
        if master_id in master_releases:
            continue

        release_data = get_main_release_data(discogs, master_id)
        if not release_data:
            resp_404.append(master_id)

        master_releases[master_id] = release_data
        if not (i % 100):
            cache.update(master_releases)

    cache.update(master_releases)

    msg = '\n\nNot found:'
    cprint(msg, 'red')
    for master_id in resp_404:
        cprint(master_id, 'red')
