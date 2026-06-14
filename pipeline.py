import os
import pandas as pd

from dataset_loader import (load_all_datasets)

from semantic_mapping import (semantic_column_mapping)

from harmonization import (harmonize_dataset)

from report_generator import generate_report

# ---------------------------------
# Complete Harmonization Pipeline
# ---------------------------------
def run_pipeline(uploaded_files):

    # --------------------------
    # Load datasets
    # --------------------------
    datasets = (load_all_datasets(uploaded_files))

    harmonized_outputs = {}

    # --------------------------
    # Process all datasets
    # --------------------------
    for (dataset_name, dataset_info) in datasets.items():

        # ---------------------------------------------------------------------
        # Extract metadata constraints dynamically for semantic_column_mapping
        # ---------------------------------------------------------------------
        df_current = dataset_info["dataframe"]
        
        # Build 10 sample structural rows formatted cleanly into a JSON string matrix
        sample_rows_json = df_current.head(10).to_json(orient='records')

        # ----------------------
        # Semantic mapping
        # ----------------------
        mapping_result = semantic_column_mapping(
            dataset_info["schema"],
            sample_rows=sample_rows_json
        )

        mapping = mapping_result["mapping"]
        reasoning = mapping_result.get("reasoning", {})

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
        os.makedirs("outputs", exist_ok=True)

        output_path = (
            f"outputs/"
            f"{dataset_name}"
            f".csv"
        )

        harmonized_df.to_csv(output_path, index=False)

        harmonized_outputs[dataset_name] = harmonized_df
        dataset_info["mapping"] = mapping
        dataset_info["reasoning"] = reasoning

    return {
        "harmonized_outputs": harmonized_outputs,
        "datasets": datasets,
        "mappings": {
            dataset_name: dataset_info.get("mapping", {})
            for dataset_name, dataset_info in datasets.items()
        },
        "reasonings": {
            dataset_name: dataset_info.get("reasoning", {})
            for dataset_name, dataset_info in datasets.items()
        }
    }
