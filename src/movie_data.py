from imdb import Cinemagoer, IMDbError


class MovieData:
    fields = {}
    chosen_fields = fields

    @classmethod
    def _register_field(cls, method, name, config=None):
        """Register an available field that can be used to query the data."""
        # if a config is supplied, it must have min, max, default
        if config and not all(c in config for c in ("min", "max", "default")):
            raise RuntimeError(f"Configuration for '{name}' field is invalid. Must specify min, max and default.")

        cls.fields[name] = {'method': method, 'config': config}

    @classmethod
    def _unregister_field(cls, name):
        """Remove a specified file from the list of available fields."""
        cls.fields.pop(name)

    @classmethod
    def get_field_names(cls):
        return cls.fields.keys()

    @classmethod
    def get_field_configs(cls):
        pass

    @classmethod
    def set_chosen_fields(cls, choices):
        pass

    @classmethod
    def set_field_limits(cls, limits):
        pass

    @classmethod
    def get_movie_data(cls, identifier):
        pass


class IMDbData(MovieData):
    """ This is the client code that specifies what Movie data is available for extraction. """
    imdb = Cinemagoer()
    BASE_URL = 'http://www.imdb.com/title/'

    # Field limits
    MAX_GENRES = 3
    MAX_COUNTRIES = 3
    MAX_CAST = 3
    MAX_LANGS = 2

    def __init__(self):
        super().__init__()
        self._register_field(self._get_title, 'Title')
        self._register_field(self._get_director, 'Director')
        self._register_field(self._get_genres, 'Genres',
                             {'label': 'Max genres', 'default': self.MAX_GENRES, 'min': 1, 'max': 9})
        self._register_field(self._get_short_synopsis, 'Synopsis (short)')
        self._register_field(self._get_full_synopsis, 'Synopsis (long)')
        self._register_field(self._get_year, 'Year')
        self._register_field(self._get_countries, 'Countries',
                             {'label': 'Max countries', 'default': self.MAX_COUNTRIES, 'min': 1, 'max': 9})
        self._register_field(self._get_cast, 'Cast',
                             {'label': 'Max cast', 'default': self.MAX_CAST, 'min': 1, 'max': 9})
        self._register_field(self._get_runtime, 'Runtime')
        self._register_field(self._get_language, 'Language',
                             {'label': 'Max languages', 'default': self.MAX_LANGS, 'min': 1, 'max': 9})
        self._register_field(self._get_rating, 'IMDb rating')
        self._register_field(self._get_imdb_id, 'IMDb ID')
        self._register_field(self._get_url, 'URL')

    @classmethod
    def set_chosen_fields(cls, choices):
        cls.chosen_fields = {field: cls.fields[field] for field in choices if field in cls.fields}

    @classmethod
    def set_field_limits(cls, limits):
        cls.MAX_GENRES = limits.get('Genres', cls.MAX_GENRES)
        cls.MAX_COUNTRIES = limits.get('Countries', cls.MAX_COUNTRIES)
        cls.MAX_CAST = limits.get('Cast', cls.MAX_CAST)
        cls.MAX_LANGS = limits.get('Languages', cls.MAX_LANGS)

    @classmethod
    def get_field_configs(cls):
        return {field: field_data['config'] for field, field_data in cls.fields.items()}

    @classmethod
    def get_movie_data(cls, identifier):
        """ Return all the requested data for a given movie if identifier is valid, otherwise return None. """
        try:
            movie = cls.imdb.get_movie(identifier)
            return cls._get_metadata(movie)
        except IMDbError:
            print(f'Invalid ID: {identifier}')

    @classmethod
    def _get_metadata(cls, movie):
        """ Gather all the requested data for the specified movie. """
        return {field: field_data.get('method')(movie) for field, field_data in cls.chosen_fields.items()}

    @classmethod
    def _get_title(cls, movie):
        return movie.get('title', 'n/a')

    @classmethod
    def _get_director(cls, movie):
        directors = movie.get('directors')
        if directors:
            return ', '.join([d['name'] for d in directors])
        else:
            return 'n/a'

    @classmethod
    def _get_genres(cls, movie):
        genres = movie.get('genres')
        if genres:
            return ', '.join([g for g in genres][:cls.MAX_GENRES])
        else:
            return 'n/a'

    @classmethod
    def _get_short_synopsis(cls, movie):
        outline = movie.get('plot outline')
        if outline:
            return outline
        else:
            outline = movie.get('plot')
            if outline:
                return outline[0]
            else:
                return 'n/a'

    @classmethod
    def _get_full_synopsis(cls, movie):
        synopsis = movie.get('synopsis')
        if synopsis:
            return synopsis[0]
        else:
            return 'n/a'

    @classmethod
    def _get_year(cls, movie):
        return movie.get('year', 'n/a')

    @classmethod
    def _get_countries(cls, movie):
        countries = movie.get('countries')
        if countries:
            return ', '.join([c for c in countries][:cls.MAX_COUNTRIES])
        else:
            return 'n/a'

    @classmethod
    def _get_cast(cls, movie):
        cast = movie.get('cast')
        if cast:
            return ', '.join([c['name'] for c in cast][:cls.MAX_CAST])
        else:
            return 'n/a'

    @classmethod
    def _get_runtime(cls, movie):
        runtimes = movie.get('runtimes')
        if runtimes:
            return runtimes[0]
        else:
            return 'n/a'

    @classmethod
    def _get_language(cls, movie):
        languages = movie.get('languages')
        if languages:
            return ', '.join([lang for lang in languages][:cls.MAX_LANGS])
        else:
            return 'n/a'

    @classmethod
    def _get_rating(cls, movie):
        return movie.get('rating', 'n/a')

    @classmethod
    def _get_imdb_id(cls, movie):
        return 'tt' + movie.get('imdbID')

    @classmethod
    def _get_url(cls, movie):
        return cls.BASE_URL + cls._get_imdb_id(movie)
