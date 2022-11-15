import itertools

import discovery.utils.dataframe_matcher

from utils.component_decorators import data
from discovery import DiscoveryClient
from discovery.utils.dataframe_matcher import DataFrameMatcher


@data("local_data_catalogue")
class LocalDataCatalogue:
    def __init__(self, config):
        self.discovery_client = DiscoveryClient({})
        self.file_path = "local_data"
        self.load_files()

        # TODO: currently this is hardcoded within the discovery project
        self.match_types = {
            "Match Identical Values": "match_data_identical_values",
            "Match Pearson Coefficient": "match_data_pearson_coefficient",
            "Match Dynamic Time Warping": "match_data_dynamic_time_warping",
            "Match Column Name (LCS)": "match_name_lcs",
            "Match Column Name (LVN)": "match_name_levenshtein",
            "Match Column Name (wordnet)": "match_name_wordnet"
        }
        # TODO: workaround logic to enable more robust matching
        self.name_match_types = {
            "Match Column Name (LCS)": "match_name_lcs",
            "Match Column Name (LVN)": "match_name_levenshtein",
            "Match Column Name (wordnet)": "match_name_wordnet"
        }
        self.col_match_types = {
            "Match Identical Values": "match_data_identical_values",
            "Match Pearson Coefficient": "match_data_pearson_coefficient",
            "Match Dynamic Time Warping": "match_data_dynamic_time_warping",
        }

    def load_files(self):
        """ load in a set of files at the data root path """
        self.discovery_client.add_files(self.file_path)
        self.discovery_client.reconstruct_metadata()

    def get_loaded_files(self):
        """ get a list of files that are loaded """
        return self.discovery_client.get_loaded_files()

    def get_dataframe_comparisons(self, comparison_types, comparison_weights, origin_df, target_df):
        """
        Get comparisons between two dataframes
        Apply given weights and average all percentages
        """
        # TODO: dataframe matcher is currently hardcoded to run 2 direct comparisons, forcing us to abstract it away
        # TODO: until comparisons are sorted out, try to minimise duplicate runs
        default_name_match = "match_name_lcs"
        default_col_match = "match_data_identical_values"
        name_matches = []
        col_matches = []
        similarities = {col: {} for col in origin_df.columns}
        for comparison in comparison_types:
            if comparison in self.name_match_types:
                name_matches.append(comparison)
            col_matches.append(comparison)

        for name_matcher, data_matcher in itertools.zip_longest(name_matches, col_matches):
            name_matcher = name_matcher or default_name_match
            data_matcher = data_matcher or default_col_match
            name_matcher = getattr(DataFrameMatcher, name_matcher)
            data_matcher = getattr(DataFrameMatcher, data_matcher)
            matcher = DataFrameMatcher(name_matcher, data_matcher)

            try:
                for similarity in matcher.match_dataframes(origin_df, target_df):
                    similarity_column = similarities[similarity['column_a']]
                    # TODO: name/data matching produces terrible results for averaging
                    similarity_avg = (similarity['name_confidence'] + similarity['data_confidence']) / 2
                    similarity_column.setdefault(similarity['column_b'], [similarity_avg]).append(similarity_avg)

            except TypeError:
                continue

        # format the outputs to be fed into the dash data table
        data_table_format = [
            {
                nested_col_name: round(sum(similarities[col_name][nested_col_name])/len(similarities[col_name][nested_col_name]), 2)
                for nested_col_name in similarities[col_name]
            }
            for col_name in target_df.columns
        ]

        return data_table_format
