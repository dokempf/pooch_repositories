from pooch.downloaders import DataRepository
from pooch.utils import parse_url


class PangaeaRepository(DataRepository):
    def __init__(self, doi, archive_url):
        self.doi = doi
        self.archive_url = archive_url
        self._dataset = None

    @property
    def pangaea_dataset(self):
        if self._dataset is None:
            # We lazily load this. This way we only expose ourselves to issues with
            # importing pangaeapy when we actually know we need it.
            import pangaeapy.pandataset as pd
            self._dataset = pd.PanDataSet(self.doi)
        return self._dataset

    @classmethod
    def initialize(cls, doi, archive_url):

        parsed_archive_url = parse_url(archive_url)
        
        if parsed_archive_url["netloc"] != "doi.pangaea.de":
            return None
        
        return cls(doi, archive_url)

    def populate_registry(self, pooch):
        # Add the tab-separated values file with the actual data
        pooch.registry[f"{self.doi}.tab"] = None
        pooch.urls[f"{self.doi}.tab"] = f"https://ws.pangaea.de/dds-fdp/rest/panquery?datasetDOI=doi.pangaea.de/{self.doi}"

        # Add all auxiliary data available
        for name, param in self.pangaea_dataset.params.items():
            if param.type == "filename":
                for filename in self.pangaea_dataset.data[name].to_list()[1:]:
                    pooch.registry[filename] = None
                    pooch.urls[filename] = f"https://download.pangaea.de/dataset/{self.pangaea_dataset.id}/files/{filename}"
