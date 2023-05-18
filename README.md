# Multithreaded IMDb Scraper with GUI

### Key Features:
* Rapid extraction of data for a specified list of IMDb IDs (tt[0-9]), individually or in bulk.
* IDs can be supplied within a CSV file, or simply pasted directly into the interface.
* User can specify exactly what fields they are interested in (genres, language, etc.), and the results are exported as a CSV.

### Technical Features:
* Multithreaded scraping for rapid performance.
* Low coupling to make it straightforward to add/remove fields, implement a new UI, broader filetype support, even reuse the project as a generic web scraper for non-IMDb applications.

### Future development plans include:
* Support more filetypes for importing IDs and exporting data.
* Implement full dependency injection