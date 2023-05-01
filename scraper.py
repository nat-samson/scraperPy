import threading

from file_handler import CsvHandler
from movie_data import IMDbData
from ui import ScraperUI

MAX_GENRES = 2
MAX_CAST = 3
MAX_LANGUAGES = 2
MAX_COUNTRIES = 2


class Scraper:
    def __init__(self, file_handler, data_source):
        self.file_handler = file_handler
        self.data_source = data_source
        self.ui = None

    def set_ui(self, ui):
        self.ui = ui

    def get_movies(self, ids):
        # TODO find a way to notify with each retrieved film
        movie_data = map(self.data_source.get_movie_data, ids)
        return filter(lambda movie: movie is not None, movie_data)

    def get_field_names(self):
        return self.data_source.get_field_names()

    def set_chosen_fields(self, chosen):
        self.data_source.set_chosen_fields(chosen)

    def get_field_configs(self):
        return self.data_source.get_field_configs()

    def set_field_configs(self, limits):
        self.data_source.set_field_limits(limits)

    def process(self, data, fields, scales, open_path=None):
        """ Check the validity of the user-submitted data and begin the processing if valid, else warn the user."""
        if not fields:
            self.ui.alert_user('No fields', 'No fields have been selected.')
            return

        if open_path:
            ids = self.file_handler.open_file(open_path)
        else:
            ids = self.file_handler.extract_ids(data)

        if not ids:
            self.ui.alert_user('No IMDb IDs', 'The submitted data contains no potential IMDb IDs.')
            return

        save_path = self.ui.ask_to_save()
        if save_path:
            # If we've got this far, let's get processing!
            self.set_chosen_fields(fields)
            self.set_field_configs(scales)
            self.ui.set_progress_max(len(ids))
            movies_data = self.get_movies(ids)
            threading.Thread(target=lambda: self.export(movies_data, fields, save_path)).start()

    def export(self, movies_data, fields, path):
        self.file_handler.save_file(movies_data, fields, self.ui.update_progress, path)


def main():
    # set up all the objects we need
    file_handler = CsvHandler('tt(\d+)')
    data_source = IMDbData()
    scraper = Scraper(file_handler, data_source)
    ui = ScraperUI(scraper)
    scraper.set_ui(ui)
    ui.mainloop()


if __name__ == '__main__':
    main()
