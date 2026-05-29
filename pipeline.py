import os
import pandas as pd

from dataset_loader import (
    load_all_datasets
)

from semantic_mapping import (
    semantic_column_mapping
)

from harmonization import (
    harmonize_dataset
)


# ---------------------------------
# Complete Harmonization Pipeline
# ---------------------------------
def run_pipeline(
    uploaded_files
):

    # --------------------------
    # Load datasets
    # --------------------------
    datasets = (
        load_all_datasets(
            uploaded_files
        )
    )

    harmonized_outputs = {}

    # -------------------------------------------------------------------------
    # Establish Template & Baseline Schema Requirements
    # -------------------------------------------------------------------------
    # Pull template structure directly from the first dataset loaded in the pipeline
    first_dataset_key = list(datasets.keys())[0] if datasets else None
    
    if first_dataset_key:
        template_cols = list(datasets[first_dataset_key]["dataframe"].columns)
    else:
        template_cols = []

    # --------------------------
    # Process all datasets
    # --------------------------
    for (
        dataset_name,
        dataset_info
    ) in datasets.items():

        # ---------------------------------------------------------------------
        # Extract metadata constraints dynamically for semantic_column_mapping
        # ---------------------------------------------------------------------
        df_current = dataset_info["dataframe"]
        
        # Build 10 sample structural rows formatted cleanly into a JSON string matrix
        sample_rows_json = df_current.head(10).to_json(orient='records')

        # ----------------------
        # Semantic mapping
        # ----------------------
        try:
            # Invoking the semantic mapping function passing all required validation bounds
            mapping = (
                semantic_column_mapping(
                    dataset_info["schema"],
                    template_columns=template_cols,
                    sample_rows=sample_rows_json
                )
            )
        except TypeError:
            # Defensive fallback path in case some structural variants pass unexpected parameters
            mapping = (
                semantic_column_mapping(
                    dataset_info["schema"]
                )
            )

        # ----------------------
        # Harmonization
        # ----------------------
        harmonized_df = (
            harmonize_dataset(
                dataset_info[
                    "dataframe"
                ],
                mapping
            )
        )

        # ----------------------
        # Save output
        # ----------------------
        os.makedirs(
            "outputs",
            exist_ok=True
        )

        output_path = (
            f"outputs/"
            f"{dataset_name}"
            f"_harmonized.csv"
        )

        harmonized_df.to_csv(
            output_path,
            index=False
        )

        harmonized_outputs[
            dataset_name
        ] = harmonized_df

    return (
        harmonized_outputs
    )


# ---------------------------------
# Run Pipeline
# ---------------------------------
if __name__ == "__main__":

    uploaded_files = [
        r"E:\NGIT\3-2 Sem\Mini Project\Dataset\Online Retail Datasets\Online Retail\online_retail.csv",
        r"E:\NGIT\3-2 Sem\Mini Project\Dataset\Online Retail Datasets\Supermarket Sales\supermarket_sales.csv"
    ]

    # Executes the pipeline cleanly without emitting console log pollution
    harmonized_results = (
        run_pipeline(
            uploaded_files
        )
    )