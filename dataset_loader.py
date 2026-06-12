import os
import pandas as pd

from preprocessing import process_dataset
from schema_generator import generate_schema

def load_all_datasets(uploaded_files):
    loaded_datasets = {}

    for file in uploaded_files:
        # ----------------------
        # Read dataset
        # ----------------------
        file_extension = os.path.splitext(file)[1].lower()
        
        # Calculate file size in MB for the report
        file_size_mb = os.path.getsize(file) / (1024 * 1024)

        if file_extension == ".csv":
            dataframe = pd.read_csv(file, low_memory=False)
        elif file_extension in [".xlsx", ".xls"]:
            dataframe = pd.read_excel(file)
        else:
            raise ValueError(f"Unsupported file format: {file}")

        # ----------------------
        # Generic preprocessing
        # ----------------------
        dataframe = process_dataset(dataframe)

        # ----------------------
        # Auto schema generation
        # ----------------------
        schema = generate_schema(dataframe.columns)

        # ----------------------
        # Dataset name
        # ----------------------
        dataset_name = os.path.splitext(os.path.basename(file))[0]

        # ----------------------
        # Package Dataset Metadata
        # ----------------------
        loaded_datasets[dataset_name] = {
            "dataframe": dataframe,
            "schema": schema,
            "sample_rows": dataframe.head(3).to_dict(orient="records"),
            # Added for the report requirements
            "file_size": f"{file_size_mb:.2f} MB"
        }

    return loaded_datasets