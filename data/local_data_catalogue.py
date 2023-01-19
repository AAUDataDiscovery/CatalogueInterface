import copy
import itertools
import os

from utils.component_decorators import data
from discovery import DiscoveryClient
from utils.directory_tree_visual import DisplayablePath
from discovery.data_matching.matching_methods import *
from discovery.data_matching.dataframe_matcher import DataFrameMatcher


@data("local_data_catalogue")
class LocalDataCatalogue:
    def __init__(self, config):
        self.discovery_client = DiscoveryClient({})
        self.file_path = "local_data"
        self.file_catalogue_ref = {}
        self.load_files()

        self.match_types = {
            "Match Identical Values": MatchIdenticalRows,
            "Match Pearson Coefficient": MatchDataPearsonCoefficient,
            "Match Dynamic Time Warping": MatchDataDynamicTimeWarping,
            "Match Column Name (LCS)": MatchColumnNamesLCS,
            "Match Column Name (LVN)": MatchColumnNamesLevenshtein,
            "Match Column Name (wordnet)": MatchColumnNamesWordnet
        }

    def load_files(self):
        """ Load in a set of files at the data root path """
        for new_item in self.discovery_client.scan_local_filesystem(self.file_path):
            self.file_catalogue_ref[new_item.get_metadata().data_manifest['path']] = new_item.get_id()
        # for root, dirs, files in os.walk(self.file_path):
        #     for filename in files:
        #         full_path = os.path.join(root, filename)
        #         if full_path not in self.discovery_client.loaded_catalogue:
        #             self.discovery_client.load_file(full_path)

    def get_loaded_files(self):
        """ Get all metadata that's in memory """
        return self.file_catalogue_ref

    def get_metadata_by_file(self, filename):
        """ Retrieve metadata from memory by file name """
        return self.discovery_client.loaded_catalogue.get(self.file_catalogue_ref[filename])

    def get_metadata_by_hash(self, data_checksum):
        """ Retrieve metadata from memory by data checksum """
        for catalogue_item in self.discovery_client.loaded_catalogue.values():
            if catalogue_item.get_checksum() == data_checksum:
                return catalogue_item

    def get_dataframe_comparisons(self, comparison_types, comparison_weights, origin_catalogue, target_catalogue,
                                  active_origin_columns, active_target_columns):
        """
        Get comparisons between two dataframes
        Apply given weights and average all percentages

        Note that with the datable format, we must preserve row order, but not column order
        """

        origin_df = origin_catalogue.get_data().reindex(columns=active_origin_columns)
        target_df = target_catalogue.get_data().reindex(columns=active_target_columns)

        origin_meta = origin_catalogue.get_metadata()
        target_meta = target_catalogue.get_metadata()

        match_methods = [self.match_types.get(method) for method in comparison_types]
        df_matcher = DataFrameMatcher()
        similarities = {}

        for origin_column, target_column in itertools.product(active_origin_columns, active_target_columns):
            similarity = df_matcher.match_columns(
                methods=match_methods,
                col_meta1=copy.copy(origin_meta.columns[origin_column]),
                col_meta2=copy.copy(target_meta.columns[target_column]),
                series1=origin_df[origin_column],
                series2=target_df[target_column],
                metadata1=copy.copy(origin_meta),
                metadata2=copy.copy(target_meta),
                weights=comparison_weights
            )
            similarities.setdefault(origin_column, {}).update({target_column: round(similarity[1], 2)})

        return similarities

    def update_relationships(self, origin_file_name, target_file_name, origin_col_name, target_col_name, certainty):
        target_catalogue = self.get_metadata_by_file(target_file_name)
        origin_catalogue = self.get_metadata_by_file(origin_file_name)

        origin_metadata = origin_catalogue.get_metadata()
        origin_metadata.columns[origin_col_name].add_relationship(certainty, target_catalogue.get_checksum(),
                                                                  target_col_name)

    def get_directory_tree(self):
        return DisplayablePath.make_tree(
            self.file_path
        )
