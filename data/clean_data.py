import re
import json
from unipath import Path
from itertools import chain

GRAPH_JSON_FILE = Path(__file__).parent.child('jazz_musicians_graph.json')


def valid_role(role):
    valid_roles = [
        'Accordion',
        'Acoustic Bass',
        'Acoustic Guitar',
        'Alto Flute',
        'Alto Recorder',
        'Alto Saxophone',
        'Alto Vocals',
        'Arco Bass',
        'Arranged & Conducted By',
        'Backing Band',
        'Backing Vocals',
        'Bagpipes',
        'Band',
        'Banjo',
        'Bansuri',
        'Baritone Saxophone',
        'Baritone Vocals',
        'Bass',
        'Bass Clarinet',
        'Bass Drum',
        'Bass Flute',
        'Bass Guitar',
        'Bass Harmonica',
        'Bass Saxophone',
        'Bass Trombone',
        'Basset Horn',
        'Bassoon',
        'Bata',
        'Bell Tree',
        'Bells',
        'Bird Calls',
        'Blues Harp',
        'Bongos',
        'Bouzouki',
        'Brass',
        'Cabaca',
        'Cabasa',
        'Cadenza',
        'Caller',
        'Carillon',
        'Castanets',
        'Cavaquinho',
        'Celesta',
        'Cello',
        'Chimes',
        'Choir',
        'Chorus',
        'Chorus Master',
        'Cimbalom',
        'Clarinet',
        'Classical Guitar',
        'Claves',
        'Clavichord',
        'Clavinet',
        'Concert Flute',
        'Concertina',
        'Conductor',
        'Congas',
        'Contrabass',
        'Contrabass Clarinet',
        'Contrabassoon',
        'Contractor',
        'Contralto Vocals',
        'Cornet',
        'Cornett',
        'Coro',
        'Cowbell',
        'Cymbal',
        'Double Bass',
        'Drum',
        'Drums',
        'Dulcitone',
        'Effects',
        'Electric Bass',
        'Electric Guitar',
        'Electric Piano',
        'Electronics',
        'English Horn',
        'Ensemble',
        'Euphonium',
        'Featuring',
        'Fiddle',
        'Finger Cymbals',
        'Flamenco Guitar',
        'Flugelhorn',
        'Flute',
        'Fortepiano',
        'French Horn',
        'Glockenspiel',
        'Goblet Drum',
        'Gong',
        'Gown',
        'Guiro',
        'Guitar',
        'Harmonica',
        'Harmony Vocals',
        'Harp',
        'Harpsichord',
        'Helicon',
        'Horn',
        'Horns',
        'Instruments',
        'Jug',
        'Kalimba',
        'Kanjira',
        'Kanun',
        'Kazoo',
        'Keyboards',
        'Koto',
        'Lead Guitar',
        'Lead Vocals',
        'Leader',
        'Lute',
        'Lyre',
        'Mandolin',
        'Manzello',
        'Maracas',
        'Marimba',
        'Marimbula',
        'Mc',
        'Mellophone',
        'Melodica',
        'Mezzo-Soprano Vocals',
        'Musician',
        'Normaphone',
        'Nose Flute',
        'Oboe',
        'Ocarina',
        'Orchestra',
        'Orchestra Bells',
        'Organ',
        'Oud',
        'Painting',
        'Pandeiro',
        'Pedal Steel Guitar',
        'Percussion',
        'Performer',
        'Piano',
        'Piccolo Flute',
        'Piccolo Trumpet',
        'Ratchet',
        'Rattle',
        'Reeds',
        'Resonator Guitar',
        'Rhythm Guitar',
        'Sarod',
        'Saxello',
        'Saxophone',
        'Scraper',
        'Scratches',
        'Shaker',
        'Shanai',
        'Shekere',
        'Siren',
        'Sitar',
        'Sleeve',
        'Sleeve Notes',
        'Snare',
        'Solo Vocal',
        'Soloist',
        'Sopranino Saxophone',
        'Soprano Saxophone',
        'Soprano Vocals',
        'Spoons',
        'Steel Drums',
        'Steel Guitar',
        'Strings',
        'Stritch',
        'Suling',
        'Synthesizer',
        'Tabla',
        'Talking Drum',
        'Tambourine',
        'Tambura',
        'Tap Dance',
        'Tape',
        'Temple Block',
        'Tenor Banjo',
        'Tenor Saxophone',
        'Tenor Vocals',
        'Theremin',
        'Timbales',
        'Timpani',
        'Tom Tom',
        'Tree Bells',
        'Tres',
        'Triangle',
        'Trombone',
        'Trumpet',
        'Tuba',
        'Twelve-String Guitar',
        'Typography',
        'Ukulele',
        'Valve Trombone',
        'Vibraphone',
        'Vibraslap',
        'Viola',
        'Violin',
        'Violoncello',
        'Vocalese',
        'Vocals',
        'Voice',
        'Voice Actor',
        'Washboard',
        'Whistle',
        'Whistling',
        'Wind',
        'Wind Chimes',
        'Wood Block',
        'Wood Logs',
        'Woodwind',
        'Xylophone',
        'Zither',
    ]
    return role.strip() in valid_roles

def clean_artist_data(artist):
    role = re.sub('\[.+\]', '', artist['role'])
    roles = [r.strip().title() for r in role.split(',') if valid_role(r)]
    data = {
        'name': artist['name'],
        'roles': roles,
    }
    return str(artist['id']), data

def clean_release_data(release):
    """
    Output example (1 item):


    {'id': 10287104,
     'musicians': {161234: {'name': 'Doc Severinsen', 'roles': ['Trumpet']},
                   272946: {'name': 'George Barnes', 'roles': ['Guitar']},
                   272947: {'name': 'Jack Lesberg', 'roles': ['Bass']},
                   312526: {'name': 'Lou McGarity',
                            'roles': ['Trombone', 'Vocals']},
                   325856: {'name': 'Dick Cary',
                            'roles': ['Piano', 'Horn', 'Trumpet']},
                   347902: {'name': 'Bob Wilber',
                            'roles': ['Clarinet', 'Tenor Saxophone', 'Clarinet']},
                   2460589: {'name': 'Don Marino', 'roles': ['Drums']}},
     'title': 'Blue Lou',
     'year': 1960}
    """
    clean_data = {
        'id': str(release['id']),
        'title': release['title'],
        'year': release['year'],
        'musicians': {},
    }

    musicians = {}
    artists = chain(release['artists'], release['extraartists'])
    for raw_artist in artists:
        id_, artist_data = clean_artist_data(raw_artist)
        if not artist_data['roles']:
            continue

        if not id_ in musicians:
            musicians[id_] = {'roles': []}

        musicians[id_]['roles'].extend(artist_data['roles'])
        musicians[id_]['name'] = artist_data['name']

    if not musicians:
        id_, artist_data = clean_artist_data(release['artists'][0])
        musicians[id_] = {'roles': []}
        musicians[id_]['name'] = artist_data['name']

    clean_data['musicians'] = musicians
    return clean_data

def get_musicians_nodes_and_rels(release_id, musicians):
    nodes, edges = {}, []

    for id_, data in musicians.items():
        edge_data = {'type': 'RECORDED', 'roles': data['roles']}
        edges.append((id_, release_id, edge_data))

        nodes[id_] = {'name': data['name'], 'roles': data['roles']}
        other_artists = dict((k, v) for k, v in musicians.items() if id_ != k)
        for other_id, other_data in other_artists.items():
            other_id = str(other_id)
            edge_data = {'type': 'PLAYED_WITH', 'roles': data['roles'], 'release_id': release_id}
            edges.append((str(id_), str(other_id), edge_data))

    return nodes, edges

def write_graph_json(releases_data):
    nodes, edges = {}, []

    for release_id, release_data in releases_data.items():
        release_node_id = '{}-{}'.format(release_id, release_data['title'])
        nodes[release_node_id] = {'title': release_data['title'], 'type': 'RELEASE', 'year': release_data['year']}
        musicians_nodes, musicians_edges = get_musicians_nodes_and_rels(
            release_node_id, release_data['musicians']
        )
        edges.extend(musicians_edges)

        for musician_id, data in musicians_nodes.items():
            if musician_id not in nodes:
                nodes[musician_id] = {'name': data['name'], 'roles': set(), 'type': 'MUSICIAN'}
            nodes[musician_id]['roles'].update(data['roles'])

    for node in [n for n in nodes.values() if 'roles' in n]:
        node['roles'] = list(node['roles'])
    with open(GRAPH_JSON_FILE, 'w') as fd:
        json_data = {'nodes': nodes, 'edges': edges}
        json.dump(json_data, fd)


if __name__ == '__main__':
    releases_json_file = Path(__file__).parent.child('master_releases.json')
    with open(releases_json_file, 'r') as fd:
        data = json.load(fd)
        releases = [r for r in data.values() if r]

    print("# of raw relases: {}".format(len(releases)))

    clean_releases = {}
    for release in releases:
        clean_data = clean_release_data(release)
        id_ = clean_data.pop('id')
        clean_releases[id_] = clean_data

    with_musicians = dict((id_, r) for id_, r in clean_releases.items() if len(r['musicians']) > 1)
    print("# of clean relases: {}".format(len(clean_releases)))
    print("# of clean relases with more than one musicians: {}".format(len(with_musicians)))

    write_graph_json(clean_releases)
    print('Graph JSON updated: "{}"'.format(GRAPH_JSON_FILE))
