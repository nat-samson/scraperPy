from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock

from file_handler import CsvHandler
from movie_data import IMDbData
from ui import ScraperUI

MAX_GENRES = 2
MAX_CAST = 3
MAX_LANGUAGES = 2
MAX_COUNTRIES = 2


class Scraper:
    def __init__(self, file_handler, data_source):
        self.executor = None
        self.file_handler = file_handler
        self.data_source = data_source
        self.ui = None
        self.cancelled = False

    def set_ui(self, ui):
        self.ui = ui

    def get_field_names(self):
        return self.data_source.get_field_names()

    def set_chosen_fields(self, chosen):
        self.data_source.set_chosen_fields(chosen)

    def get_field_configs(self):
        return self.data_source.get_field_configs()

    def set_field_configs(self, limits):
        self.data_source.set_field_limits(limits)

    def process(self, movies_data, fields, scales, open_path=None):
        """ Check the validity of the user-submitted data and begin the processing if valid, else warn the user."""
        if not fields:
            self.ui.alert_user('No fields', 'No fields have been selected.')
            return

        if open_path:
            ids = self.file_handler.open_file(open_path)
        else:
            ids = self.file_handler.extract_ids(movies_data)

        if not ids:
            self.ui.alert_user('No IMDb IDs', 'The submitted data contains no potential IMDb IDs.')
            return

        save_path = self.ui.ask_to_save()
        if save_path:
            # If we've got this far, let's get processing!
            self.set_chosen_fields(fields)
            self.set_field_configs(scales)
            self.ui.set_progress_max(len(ids))
            self.cancelled = False
            lock = Lock()

            self.executor = ThreadPoolExecutor()
            movies_data = self.executor.map(self._get_movie, ids)
            Thread(target=self._export, args=(movies_data, fields, save_path)).start()

    def _get_movie(self, identifier):
        """Returns movie data for given identifier or None if identifier was invalid."""
        return self.data_source.get_movie_data(identifier), identifier

    def _export(self, movies, fields, path):
        """Collects the movie data and writes it out to specified file path, notifying the UI as it goes."""
        results = []
        for movie in movies:
            if self.cancelled:
                break
            elif movie[0]:
                results.append(movie[0])
                self.ui.update_progress(movie[0]['Title'])  # todo this is tightly coupled to data representation
            else:
                self.ui.update_progress(movie[1])

        self.executor.shutdown(cancel_futures=True)
        self.file_handler.save_file(results, fields, path)


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
