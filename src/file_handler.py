import csv
import re
from abc import ABC, abstractmethod


class FileHandler(ABC):
    @abstractmethod
    def open_file(self, path):
        pass

    @abstractmethod
    def save_file(self, data, fields, path):
        pass

    @abstractmethod
    def extract_ids(self, text):
        pass


class CsvHandler(FileHandler):
    def __init__(self, pattern):
        self.pattern = pattern

    def open_file(self, path):
        """ Identify all potential IDs from anywhere within a CSV, return them as a set. """
        ids = set()

        with open(path, newline='') as csv_input:
            reader = csv.reader(csv_input)

            for row in reader:
                matches = self.extract_ids(''.join(row))
                ids.update(matches)

        return ids

    def save_file(self, data, fields, path='output.csv'):
        """ Save the retrieved movie data as a CSV at the path specified. """
        with open(path, 'w', newline='') as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=fields)
            writer.writeheader()
            for movie in data:
                writer.writerow(movie)

    def extract_ids(self, text):
        """ Identify all potential IDs from a block of text, return them as a set. """
        return set(re.findall(self.pattern, text))
