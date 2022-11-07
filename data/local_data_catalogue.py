from utils.component_decorators import data
from discovery import DiscoveryClient


@data("local_data_catalogue")
class LocalDataCatalogue:
    def __init__(self, config):
        self.discovery_client = DiscoveryClient({})
        self.file_path = "local_data"
        self.load_files()

    def load_files(self):
        self.discovery_client.add_files(self.file_path)
        self.discovery_client.reconstruct_metadata()

    def get_loaded_files(self):
        return self.discovery_client.get_loaded_files()
