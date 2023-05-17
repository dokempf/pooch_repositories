import json
import os
import re

from pooch.downloaders import DataRepository, DataverseRepository


class Re3dataDispatchRepository(DataRepository):
    """Re3data-based dispatch to data repository implementations

    This "data repository" does not implement an actual data repository
    API. Instead it implements a lookup in the Re3data database to very
    efficiently dispatch to the correct data repository implementation
    without sending requests to the data repository.
    """

    # A flag whether we have already loaded the data
    _data_loaded = False

    # The regexes that we use to match re3data
    _dataverse_regex = None

    @classmethod
    def initialize(cls, doi, archive_url):
        # Lazily construct the required regexes
        if not cls._data_loaded:
            # Load the shipped database file
            datafile = os.path.join(
                os.path.dirname(__file__), "data", "re3data_software.json"
            )
            with open(datafile, "r") as f:
                software_data = json.load(f)

            # Construct the required regexes
            cls._dataverse_regex = re.compile("|".join(software_data["Dataverse"]))

            cls._data_loaded = True

        # Check for a match
        if cls._dataverse_regex.match(archive_url):
            return DataverseRepository(doi, archive_url)
