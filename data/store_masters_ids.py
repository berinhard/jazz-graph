###################################
# This is script is responsible for retrieve all masters ids from a very
# specific Discog's search query which is not supported by it Database API.
# It gets all the masters ids for masters returned by this query and writes
# them into a JSON file.
###################################
import requests
from lxml import html
from termcolor import cprint
from time import sleep
from unipath import Path


if __name__ == '__main__':
    base_url = r'https://www.discogs.com/search/?limit=250&sort=title%2Casc&q=&format_exact=Album&country_exact=US&genre_exact=Jazz&type=master&decade=1960&page={}'

    masters_file = Path(__file__).parent.child('masters_ids.txt')
    with open(masters_file, 'w') as fd:
        page = 0
        while True:
            page += 1
            msg = 'Importing page #{}'.format(page)
            cprint(msg, 'yellow')

            url = base_url.format(page)
            response = requests.get(url)
            content = response.content

            if not response.ok:
                msg = 'Error: {}\n\n{}'.format(response.status_code, content)
                cprint(msg, 'red')
                break

            tree = html.fromstring(content)
            masters = tree.xpath('//div[@data-id]')
            masters_ids = [r.get('data-object-id').strip() + '\n' for r in masters]
            fd.writelines(masters_ids)

            msg = '\tSleeping for while......'
            cprint(msg, 'white')
            sleep(30)
