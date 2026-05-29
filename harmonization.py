import pandas as pd

# ---------------------------------
# Automatic Harmonization Function
# ---------------------------------
def harmonize_dataset(
    dataframe,
    mapping_results,
    template_schema=None  # Added to match the pipeline signature
):
    rename_mapping = {}

    # --------------------------
    # Keep valid mappings only
    # --------------------------
    for (
        source_col,
        target_col
    ) in mapping_results.items():

        if (
            target_col
            != "UNKNOWN"
        ):

            rename_mapping[
                source_col
            ] = target_col

    # --------------------------
    # Rename columns
    # --------------------------
    harmonized_df = (
        dataframe.rename(
            columns=
            rename_mapping
        )
    )

    # --------------------------
    # Remove duplicates
    # --------------------------
    harmonized_df = (
        harmonized_df.loc[
            :,
            ~harmonized_df
            .columns
            .duplicated()
        ]
    )

    return (
        harmonized_df
    )