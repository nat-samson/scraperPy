import threading

from file_handler import CsvHandler
from movie_data import IMDbData
from ui import ScraperUI

MAX_GENRES = 2
MAX_CAST = 3
MAX_LANGUAGES = 2
MAX_COUNTRIES = 2


class Scraper:
    def __init__(self, file_handler, data_source, ui):
        self.file_handler = file_handler
        self.data_source = data_source
        self.ui = ui
        self.movies_data = {}
        self.fields = []
        self.id_count = 0

    """def extract_ids(self, ids):
        return self.file_handler.extract_ids(ids)"""

    def get_movies(self, ids):
        # TODO find a way to notify with each retrieved film
        movie_data = map(self.data_source.get_movie_data, ids)
        return filter(lambda movie: movie is not None, movie_data)

    def get_field_names(self):
        return self.data_source.get_field_names()

    def set_chosen_fields(self, chosen):
        self.data_source.set_chosen_fields(chosen)

    def process(self, data, fields, open_path=None):
        """ Issue appropriate response to inputs"""
        if open_path:
            ids = self.file_handler.open_file(open_path)
            print(ids)
        else:
            ids = self.file_handler.extract_ids(data)
            print(ids)

        if ids:
            # TODO temporary, replace with proper field submission via ui
            self.id_count = len(ids)
            fields = self.get_field_names()
            self.set_chosen_fields(fields)
            self.movies_data = self.get_movies(ids)

            # TODO alert UI that the process is done!
            save_path = self.ui.ask_to_save()
            if save_path:
                print(save_path)
                threading.Thread(target=lambda: self.export(fields, save_path)).start()
            else:
                print(save_path)
        else:
            self.ui.alert_user('No IMDb IDs', 'The submitted data contains no potential IMDb IDs.')

    def export(self, fields, path):
        self.file_handler.save_file(self.movies_data, fields, path)

    def get_id_count(self):
        return self.id_count


def main():
    # set up all the objects we need
    file_handler = CsvHandler('tt(\d+)')
    data_source = IMDbData()
    ui = ScraperUI()
    scraper = Scraper(file_handler, data_source, ui)
    ui.set_scraper(scraper)
    ui.mainloop()


if __name__ == '__main__':
    main()
