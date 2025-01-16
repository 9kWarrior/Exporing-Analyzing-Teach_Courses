import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def replace_matches_in_column(df, col, string_to_match, replacing, min_ratio=50):
    exploded_df = df.explode(column=col)
    strings = exploded_df[col].unique()

    matches = fuzzywuzzy.process.extract(string_to_match, strings,
                                         limit=30, scorer=fuzzywuzzy.fuzz.token_sort_ratio)
    close_matches = [matches[0] for matches in matches if matches[1] >= min_ratio]
    rows_with_matches = exploded_df[col].isin(close_matches)

    exploded_df.loc[rows_with_matches] = replacing
    imploded_column = exploded_df.groupby(exploded_df.index).agg({col: lambda x: x.tolist()})
    df[col] = imploded_column