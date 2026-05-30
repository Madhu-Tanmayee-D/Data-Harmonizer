import json
import os
import pandas as pd
import requests  # Used to communicate with a cloud LLM API

try:
    import streamlit as st
except Exception:
    st = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
OPENAI_API_TIMEOUT = int(os.getenv("OPENAI_API_TIMEOUT", "30"))

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "").strip()
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "google/flan-t5-large").strip()
HUGGINGFACE_API_BASE = os.getenv("HUGGINGFACE_API_BASE", "https://api-inference.huggingface.co").rstrip("/")
HUGGINGFACE_API_TIMEOUT = int(os.getenv("HUGGINGFACE_API_TIMEOUT", "30"))

if st is not None:
    def get_st_secret(key, default="", section=None):
        try:
            if section is not None:
                section_data = st.secrets.get(section, {})
                if isinstance(section_data, dict):
                    return str(section_data.get(key, default)).strip()
            return str(st.secrets.get(key, default)).strip()
        except Exception:
            return str(default).strip()

    OPENAI_API_KEY = OPENAI_API_KEY or get_st_secret("api_key", "", section="openai") or get_st_secret("OPENAI_API_KEY", "")
    OPENAI_MODEL = OPENAI_MODEL or get_st_secret("model", "gpt-4o-mini", section="openai") or get_st_secret("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_BASE = OPENAI_API_BASE or get_st_secret("api_base", "https://api.openai.com/v1", section="openai").rstrip("/") or get_st_secret("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    OPENAI_API_TIMEOUT = int(get_st_secret("api_timeout", OPENAI_API_TIMEOUT, section="openai") or OPENAI_API_TIMEOUT)

    HUGGINGFACE_API_KEY = HUGGINGFACE_API_KEY or get_st_secret("api_key", "", section="huggingface") or get_st_secret("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL = HUGGINGFACE_MODEL or get_st_secret("model", "google/flan-t5-large", section="huggingface") or get_st_secret("HUGGINGFACE_MODEL", "google/flan-t5-large")
    HUGGINGFACE_API_BASE = HUGGINGFACE_API_BASE or get_st_secret("api_base", "https://api-inference.huggingface.co", section="huggingface").rstrip("/") or get_st_secret("HUGGINGFACE_API_BASE", "https://api-inference.huggingface.co").rstrip("/")
    HUGGINGFACE_API_TIMEOUT = int(get_st_secret("api_timeout", HUGGINGFACE_API_TIMEOUT, section="huggingface") or HUGGINGFACE_API_TIMEOUT)

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
    # Phase 3: Route payload to a cloud LLM API
    # ------------------------------------------------------------
    try:
        if OPENAI_API_KEY:
            url = f"{OPENAI_API_BASE}/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 1024
            }
            api_timeout = OPENAI_API_TIMEOUT

            print("\n[DEBUG] Sending request to OpenAI-compatible cloud LLM API... please wait...")
        elif HUGGINGFACE_API_KEY:
            url = f"{HUGGINGFACE_API_BASE}/models/{HUGGINGFACE_MODEL}"
            headers = {
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.0
                },
                "options": {
                    "wait_for_model": True
                }
            }
            api_timeout = HUGGINGFACE_API_TIMEOUT

            print("\n[DEBUG] Sending request to Hugging Face inference API... please wait...")
        else:
            raise ValueError("OPENAI_API_KEY or HUGGINGFACE_API_KEY environment variable is required for cloud LLM calls.")

        response = requests.post(url, headers=headers, json=payload, timeout=api_timeout)
        response.raise_for_status()

        response_json = response.json()
        if isinstance(response_json, dict) and "choices" in response_json:
            llm_output = response_json["choices"][0]["message"]["content"].strip()
        elif isinstance(response_json, dict) and "generated_text" in response_json:
            llm_output = response_json["generated_text"].strip()
        elif isinstance(response_json, list) and response_json:
            first = response_json[0]
            if isinstance(first, dict) and "generated_text" in first:
                llm_output = first["generated_text"].strip()
            else:
                llm_output = response.text.strip()
        else:
            llm_output = response.text.strip()

        parsed_mapping = json.loads(llm_output)
        mapping_results.update(parsed_mapping)
        print("[DEBUG] Cloud LLM responded successfully!")

    except requests.exceptions.Timeout:
        print("\n[WARNING] Cloud LLM request timed out! Falling back to UNKNOWN mappings.")
        for col in columns_to_evaluate.keys():
            if col not in mapping_results:
                mapping_results[col] = "UNKNOWN"

    except Exception as e:
        print(f"\n[WARNING] Cloud LLM connection error: {str(e)}. Falling back to UNKNOWN.")
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