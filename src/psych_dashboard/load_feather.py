import pandas as pd
from psych_dashboard.app import indices


def load_feather(df_loaded):
    """
    Utility function for the common task of reading DF from feather file, and setting the MultiIndex. This is called
    every time the main DF needs to be accessed.
    """
    dff = pd.read_feather('df.feather')

    if df_loaded and len(dff) > 0:
        dff.set_index(indices, inplace=True)
    return dff


def load_filtered_feather(df_loaded):
    """
    Utility function for the common task of reading DF from feather file, and setting the MultiIndex. This is called
    every time the main DF, filtered by missing values, needs to be accessed.
    """
    dff = pd.read_feather('df_filtered.feather')

    if df_loaded and len(dff) > 0:
        dff.set_index(indices, inplace=True)
    return dff


def load_corr(df_loaded):
    """
    Utility function for the common task of reading correlation DF from feather file, and setting the MultiIndex. This is called
    every time the main DF, filtered by missing values, needs to be accessed.
    """
    dff = pd.read_feather('corr.feather')

    if df_loaded and len(dff) > 0:
        dff.set_index('index', inplace=True)
    return dff


def load_pval(df_loaded):
    """
    Utility function for the common task of reading p-value DF from feather file, and setting the MultiIndex. This is called
    every time the main DF, filtered by missing values, needs to be accessed.
    """
    dff = pd.read_feather('pval.feather')

    if df_loaded and len(dff) > 0:
        dff.set_index('index', inplace=True)
    return dff


def load_logs(df_loaded):
    """
    Utility function for the common task of reading manhattan logs DF from feather file, and setting the index.
    """
    dff = pd.read_feather('logs.feather')

    if df_loaded and len(dff) > 0:
        dff.set_index('index', inplace=True)
    return dff


def load_flattened_logs(df_loaded):
    """
    Utility function for the common task of reading flattened manhattan logs DF from feather file, and setting the index.
    """
    dff = pd.read_feather('flattened_logs.feather')

    if df_loaded and len(dff) > 0:
        dff.set_index(['first', 'second'], inplace=True)
    return dff['value']
