import os

from utils.component_decorators import data
from utils.directory_tree_visual import DisplayablePath
from discovery.utils.datagen import FakeDataGen


@data("local_data_generator")
class LocalDataGenerator:
    def __init__(self, config):
        self.local_data_path = "local_data"
        self.datagen = FakeDataGen()

    def get_directory_tree(self):
        return DisplayablePath.make_tree(
            self.local_data_path
        )

    def generate_fake_data(self, *generation_args):
        """
        Build the fake data
        The filename needs to be changed to be relative to the file path
        """
        relative_path = os.path.join(self.local_data_path, generation_args[1])
        generation_args = (generation_args[0], relative_path, *generation_args[2:])
        self.datagen.build_df_to_file(*generation_args)

