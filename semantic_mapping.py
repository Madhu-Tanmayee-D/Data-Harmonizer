import json
import pandas as pd
import requests  # Used to communicate with a local LLM via Ollama

# ---------------------------------
# Load template configuration
# ---------------------------------
with open(
    "templates/canonical_template.json",
    "r"
) as file:

    template_columns = json.load(
        file
    )


# ---------------------------------
# Function for LLM-based matching
# ---------------------------------
def semantic_column_mapping(
    dataset_columns,
    template_columns,
    sample_rows          
):
    # Ignore Columns
    with open(
        "templates/ignore_columns.json",
        "r"
    ) as file:

        IGNORE_COLUMNS = set(
            json.load(file)
        )
    
    # Rule Based Mapping
    with open(
        "templates/rule_based_mapping.json",
        "r"
    ) as file:

        RULE_BASED_MAPPING = json.load(
            file
        )

    mapping_results = {}
    columns_to_evaluate = {}

    # ------------------------------------------------------------
    # Phase 1: Short-circuit Evaluation (Pre-filtering rules)
    # ------------------------------------------------------------
    for dataset_col, description in dataset_columns.items():
        if dataset_col in IGNORE_COLUMNS:
            mapping_results[dataset_col] = "UNKNOWN"
            continue

        if dataset_col in RULE_BASED_MAPPING:
            mapping_results[dataset_col] = RULE_BASED_MAPPING[dataset_col]
            continue

        columns_to_evaluate[dataset_col] = description

    if not columns_to_evaluate:
        return mapping_results

    # ------------------------------------------------------------
    # FIX: Helper function to convert Timestamp objects to strings
    # ------------------------------------------------------------
    def json_serializable_fallback(obj):
        if hasattr(obj, "isoformat"):  # Works for both Timestamp and normal dates
            return obj.isoformat()
        if pd.isna(obj):  # Handles any missing/NaN cell data cleanly as null
            return None
        return str(obj)

    # ------------------------------------------------------------
    # Phase 2: Construct Agent Prompt with Schema + Data Samples
    # ------------------------------------------------------------
    prompt = f"""
    You are an expert Data Engineering Agent. Your task is to map incoming dataset columns to a target canonical template schema.
    
    Target Canonical Template (Available Targets):
    {json.dumps(template_columns, indent=2)}
    
    Source Columns to Map (with descriptions):
    {json.dumps(columns_to_evaluate, indent=2)}
    
    Sample Data Record Examples (Use these values to understand context if headers are messy/obscure):
    {json.dumps(sample_rows, indent=2, default=json_serializable_fallback)}
    
    CRITICAL INSTRUCTIONS:
    1. Match each source column to the most appropriate target column key from the Canonical Template.
    2. If a source column cannot possibly fit into any target, map it to "UNKNOWN".
    3. Return your response ONLY as a strictly valid flat JSON object where keys are the source columns and values are the target matches.
    4. Do not include markdown blocks, introductory greetings, or summary explanations.
    """

    # ------------------------------------------------------------
    # Phase 3: Route payload to local LLM via Ollama API
    # ------------------------------------------------------------
    try:
        # Using explicit IP 127.0.0.1 to avoid Windows localhost routing glitches
        url = "http://127.0.0.1:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "format": "json"  
        }
        
        print("\n[DEBUG] Sending request to Ollama... please wait...")
        # Added timeout=30 so if it doesn't answer in 30 seconds, it safely skips instead of freezing
        response = requests.post(url, json=payload, timeout=30)
        
        response_json = response.json()
        llm_output = response_json.get("response", "{}")
        
        parsed_mapping = json.loads(llm_output)
        mapping_results.update(parsed_mapping)
        print("[DEBUG] Ollama responded successfully!")

    except requests.exceptions.Timeout:
        print("\n[WARNING] Ollama request timed out! Falling back to UNKNOWN mappings.")
        for col in columns_to_evaluate.keys():
            if col not in mapping_results:
                mapping_results[col] = "UNKNOWN"

    except Exception as e:
        print(f"\n[WARNING] Ollama connection error: {str(e)}. Falling back to UNKNOWN.")
        for col in columns_to_evaluate.keys():
            if col not in mapping_results:
                mapping_results[col] = "UNKNOWN"

    return mapping_results


from harmonization import (
    harmonize_dataset
)

from dataset_loader import (
    load_all_datasets
)


def run_semantic_mapping(
    uploaded_files
):

    datasets = (
        load_all_datasets(
            uploaded_files
        )
    )

    all_mappings = {}

    for (
        dataset_name,
        dataset_info
    ) in datasets.items():

        mapping = (
            semantic_column_mapping(
                dataset_info[
                    "schema"
                ],
                template_columns,
                dataset_info[
                    "sample_rows"
                ]
            )
        )

        all_mappings[
            dataset_name
        ] = mapping

    template_schema = list(
        template_columns.keys()
    )

    harmonized_datasets = []

    for (
        dataset_name,
        dataset_info
    ) in datasets.items():

        harmonized_df = (
            harmonize_dataset(
                dataset_info[
                    "dataframe"
                ],

                all_mappings[
                    dataset_name
                ],

                template_schema
            )
        )

        harmonized_datasets.append(
            harmonized_df
        )

    # ------------------------------------------------------------
    # OPTIMIZATION FIX: Memory-Safe Concatenation & Duplication Check
    # ------------------------------------------------------------
    unified_dataset = pd.concat(
        harmonized_datasets,
        ignore_index=True
    )

    # Find columns that are part of our official template schema
    # (Excludes "UNKNOWN" groupings from crushing the deduplication index)
    valid_matching_columns = [
        col for col in unified_dataset.columns 
        if col in template_schema
    ]

    if valid_matching_columns:
        # Deduplicate based only on columns we actually care about
        unified_dataset = (
            unified_dataset
            .drop_duplicates(subset=valid_matching_columns)
        )
    else:
        # Secure fallback if everything failed to map
        unified_dataset = (
            unified_dataset
            .drop_duplicates()
        )

    # Free up memory immediately
    del harmonized_datasets
    
    unified_dataset.to_csv(
        "outputs/unified_dataset.csv",
        index=False
    )

    return (
        unified_dataset,
        all_mappings
    )