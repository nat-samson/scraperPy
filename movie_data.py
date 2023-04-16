from imdb import Cinemagoer, IMDbError


class MovieData:
    fields = {}
    chosen_fields = fields

    def __init__(self):
        pass

    @classmethod
    def register_field(cls, method, name):
        # private
        cls.fields[name] = method

    @classmethod
    def unregister_field(cls, name):
        # private
        cls.fields.pop(name)

    @classmethod
    def get_field_names(cls):
        return cls.fields.keys()

    @classmethod
    def set_chosen_fields(cls, choices):
        pass

    @classmethod
    def get_movie_data(cls, identifier):
        pass


class IMDbData(MovieData):
    """ This is the client code that specifies what Movie data is available for extraction. """
    imdb = Cinemagoer()
    BASE_URL = 'http://www.imdb.com/title/'

    def __init__(self):
        super().__init__()
        # TODO potentially make this a singleton
        self.register_field(self.get_title, 'Title')
        self.register_field(self.get_director, 'Director')
        self.register_field(self.get_genres, 'Genres')
        self.register_field(self.get_synopsis, 'Synopsis')
        self.register_field(self.get_year, 'Year')
        self.register_field(self.get_countries, 'Countries')
        self.register_field(self.get_cast, 'Cast')
        self.register_field(self.get_runtime, 'Runtime')
        self.register_field(self.get_language, 'Language')
        self.register_field(self.get_rating, 'Rating')
        self.register_field(self.get_imdb_id, 'IMDb ID')
        self.register_field(self.get_url, 'URL')

    @classmethod
    def set_chosen_fields(cls, choices):
        cls.chosen_fields = {field: cls.fields[field] for field in choices if field in cls.fields}

    @classmethod
    def get_movie_data(cls, identifier):
        """ Return all the requested data for a given movie if identifier is valid, otherwise return None. """
        try:
            movie = cls.imdb.get_movie(identifier)
            return cls.get_metadata(movie)
        except IMDbError:
            print(f'Invalid ID: {identifier}')

    @classmethod
    def get_metadata(cls, movie):
        """ Gather all the requested data for the specified movie. """
        return {field: method(movie) for field, method in cls.chosen_fields.items()}

    @classmethod
    def get_title(cls, movie):
        return movie.get('title', 'n/a')

    @classmethod
    def get_director(cls, movie):
        directors = movie.get('directors')
        if directors:
            return ', '.join([d['name'] for d in directors])
        else:
            return 'n/a'

    @classmethod
    def get_genres(cls, movie, limit=3):
        genres = movie.get('genres')
        if genres:
            return ' / '.join([g for g in genres][:limit])
        else:
            return 'n/a'

    @classmethod
    def get_synopsis(cls, movie):
        synopsis = movie.get('synopsis')
        if synopsis:
            return synopsis[0]
        else:
            return 'n/a'

    @classmethod
    def get_year(cls, movie):
        return movie.get('year', 'n/a')

    @classmethod
    def get_countries(cls, movie, limit=2):
        countries = movie.get('countries')
        if countries:
            return ', '.join([c for c in countries][:limit])
        else:
            return 'n/a'

    @classmethod
    def get_cast(cls, movie, limit=3):
        cast = movie.get('cast')
        if cast:
            return ', '.join([c['name'] for c in cast][:limit])
        else:
            return 'n/a'

    @classmethod
    def get_runtime(cls, movie):
        runtimes = movie.get('runtimes')
        if runtimes:
            return runtimes[0]
        else:
            return 'n/a'

    @classmethod
    def get_language(cls, movie, limit=2):
        languages = movie.get('languages')
        if languages:
            return ', '.join([lang for lang in languages][:limit])
        else:
            return 'n/a'

    @classmethod
    def get_rating(cls, movie):
        return movie.get('rating', 'n/a')

    @classmethod
    def get_imdb_id(cls, movie):
        return 'tt' + movie.get('imdbID')

    @classmethod
    def get_url(cls, movie):
        return cls.BASE_URL + cls.get_imdb_id(movie)
