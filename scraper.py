import csv
import re

from imdb import Cinemagoer, IMDbError

ia = Cinemagoer()
BASE_URL = 'http://www.imdb.com/title/'
MAX_GENRES = 2
MAX_CAST = 3
MAX_LANGUAGES = 2


# TODO improve this to not be bound to csv implementation
# perhaps create version that turns csv into just text, then another def that identifies all the csvs
def extract_ids(raw_input):
    pattern = 'tt(\d+)'
    ids = []

    with open(raw_input, newline='') as csv_input:
        reader = csv.reader(csv_input)

        for row in reader:
            imdb_id = re.search(pattern, ''.join(row))
            if imdb_id is None:
                print('Invalid ID:', row)
            else:
                ids.append(imdb_id.group(1))

    return ids


def process(movie):
    pass


def get_movie(imdb_id):
    """ Return IMDb object if ID is valid, otherwise return None. """
    try:
        return ia.get_movie(imdb_id)
    except IMDbError:
        print(f'Invalid ID: {imdb_id}')


def get_title(movie):
    return movie.get('title', 'n/a')


def get_director(movie):
    directors = movie.get('directors')
    if directors:
        return ', '.join([d['name'] for d in directors])
    else:
        return 'n/a'


def get_genres(movie, limit=3):
    genres = movie.get('genres')
    if genres:
        return ' / '.join([g for g in genres][:limit])
    else:
        return 'n/a'


def get_synopsis(movie):
    synopsis = movie.get('synopsis')
    if synopsis:
        return synopsis[0]
    else:
        return 'n/a'


def get_year(movie):
    return movie.get('year', 'n/a')


def get_countries(movie, limit=2):
    countries = movie.get('countries')
    if countries:
        return ', '.join([c for c in countries][:limit])
    else:
        return 'n/a'


def get_cast(movie, limit=3):
    cast = movie.get('cast')
    if cast:
        return ', '.join([c['name'] for c in cast][:limit])
    else:
        return 'n/a'


def get_runtime(movie):
    runtimes = movie.get('runtimes')
    if runtimes:
        return runtimes[0]
    else:
        return 'n/a'


def get_language(movie, limit=2):
    languages = movie.get('languages')
    if languages:
        return ', '.join([l for l in languages][:limit])
    else:
        return 'n/a'


def get_rating(movie):
    return movie.get('rating', 'n/a')


def get_imdb_id(movie):
    return 'tt' + movie.get('imdbID')


def get_url(movie):
    return BASE_URL + get_imdb_id(movie)


def export(film_data, fields):
    with open('output.csv', 'w', newline='') as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=fields)

        writer.writeheader()
        # film data is a list of dictionaries, might be easier to just use lists
        for film in film_data:
            writer.writerow(film)


def main():
    pass


if __name__ == '__main__':
    main()
