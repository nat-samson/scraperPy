from unittest import TestCase

from imdb import Cinemagoer

from scraper import extract_ids, get_title, get_movie, get_year, get_countries, get_director, get_cast, get_runtime, \
    get_genres, get_rating, get_language

ia = Cinemagoer()
movie_id = '0133093'
movie = ia.get_movie(movie_id)


class Test(TestCase):
    def setUp(self):
        self.pattern = None

    def test_extract_ids(self):
        expected = ['3011960', '2463288', '1615147', '4440644']
        actual = extract_ids('test.csv')

        self.assertListEqual(expected, actual)

    def test_get_movie_valid(self):
        expected = 'Hangman'
        actual = get_movie('3011960').get('title')
        self.assertEqual(expected, actual)

    def test_get_movie_invalid(self):
        actual = get_movie('0000000')
        self.assertIsNone(actual)

    def test_get_title(self):
        expected = 'The Matrix'
        actual = get_title(movie)
        self.assertEqual(expected, actual)

    def test_get_synopsis(self):
        actual = get_title(movie)
        self.assertIsInstance(actual, str)
        self.assertIn('Matrix', actual)

    def test_get_year(self):
        expected = 1999
        actual = get_year(movie)
        self.assertEqual(expected, actual)

    def test_get_countries(self):
        expected = 'United States, Australia'
        actual = get_countries(movie)
        self.assertEqual(expected, actual)

    def test_get_director(self):
        expected = 'Lana Wachowski, Lilly Wachowski'
        actual = get_director(movie)
        self.assertEqual(expected, actual)

    def test_get_cast(self):
        expected = 'Keanu Reeves, Laurence Fishburne'
        actual = get_cast(movie, 2)
        self.assertEqual(expected, actual)

    def test_get_runtime(self):
        expected = '136'
        actual = get_runtime(movie)
        self.assertEqual(expected, actual)

    def test_get_genres(self):
        expected = 'Action / Sci-Fi'
        actual = get_genres(movie)
        self.assertEqual(expected, actual)

    def test_get_rating(self):
        # rating subject to change
        actual = float(get_rating(movie))
        self.assertLessEqual(actual, 10)
        self.assertGreaterEqual(actual, 0)

    def test_get_language(self):
        expected = 'English'
        actual = get_language(movie)
        self.assertEqual(expected, actual)

    def test_export(self):
        self.fail()

    def test_process(self):
        self.fail()
