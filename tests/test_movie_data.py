from unittest import TestCase

from src.movie_data import IMDbData


class TestIMDbData(TestCase):
    def setUp(self):
        self.imdb = IMDbData()

    def test_set_chosen_fields(self):
        choices = ['Title', 'URL']
        self.imdb.set_chosen_fields(choices)
        expected = {'Title': self.imdb._get_title, 'URL': self.imdb.get_url}
        actual = self.imdb.chosen_fields
        self.assertDictEqual(expected, actual)

    def test_get_movie_data(self):
        choices = ['Title', 'Cast', 'Director', 'URL']
        self.imdb.set_chosen_fields(choices)
        expected = {'Title': 'The Matrix', 'Cast': 'Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss',
                    'Director': 'Lana Wachowski, Lilly Wachowski', 'URL': 'http://www.imdb.com/title/tt0133093'}
        actual = self.imdb.get_movie_data('0133093')
        self.assertDictEqual(expected, actual)

    def test_get_movie_data_invalid(self):
        actual = self.imdb.get_movie_data('999')
        self.assertIs(None, actual)
