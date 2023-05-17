from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from file_handler import CsvHandler
from movie_data import IMDbData
from ui import ScraperUI


class Scraper:
    def __init__(self, file_handler, data_source):
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

    def cancel(self):
        """Interrupt the current scraping process."""
        self.cancelled = True

    def process(self, movies_data, fields, scales, open_path=None):
        """ Check the validity of the user-submitted data and begin the processing if valid, else warn the user."""
        if not fields:
            self.ui.alert_user('No fields', 'No fields have been selected.')
            return

        if open_path:
            # user wants to work from a file
            ids = self.file_handler.open_file(open_path)
        else:
            # user wants to work from data pasted into the UI
            ids = self.file_handler.extract_ids(movies_data)

        if not ids:
            self.ui.alert_user('No IMDb IDs', 'The submitted data contains no potential IMDb IDs.')
            return

        # looking good so far, prompt the user for a save location
        save_path = self.ui.ask_to_save()

        if save_path:
            # If we've got this far, let's get processing!
            self.set_chosen_fields(fields)
            self.set_field_configs(scales)
            self.ui.set_progress_bar_max(len(ids))
            self.cancelled = False

            # set up the thread pool and isolate the processing from the UI
            executor = ThreadPoolExecutor()
            movies_data = executor.map(self._get_movie, ids)
            Thread(target=self._export, args=(movies_data, fields, save_path, executor)).start()

    def _get_movie(self, identifier):
        """Returns movie data for given identifier or None if identifier was invalid."""
        return self.data_source.get_movie_data(identifier), identifier

    def _export(self, movies, fields, path, executor):
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

        executor.shutdown(cancel_futures=True)
        self.file_handler.save_file(results, fields, path)


def main():
    # set up all the objects we need
    regex = 'tt(\d+)'
    file_handler = CsvHandler(regex)
    data_source = IMDbData()
    scraper = Scraper(file_handler, data_source)
    ui = ScraperUI(scraper)
    scraper.set_ui(ui)

    # start the program
    ui.mainloop()


if __name__ == '__main__':
    main()
