import json
import os
import pandas as pd
import requests  # Used to communicate with a cloud LLM API
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

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

def get_st_secret(key, default="", section=None):
    """Safely retrieve Streamlit secrets, with graceful fallback."""
    if st is None:
        return str(default).strip()
    try:
        if section is not None:
            section_data = st.secrets.get(section, {})
            if isinstance(section_data, dict):
                return str(section_data.get(key, default)).strip()
        return str(st.secrets.get(key, default)).strip()
    except Exception:
        return str(default).strip()

def _load_st_secrets():
    """Load Streamlit secrets after app initialization, suppressing warnings."""
    global OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_BASE, OPENAI_API_TIMEOUT
    global HUGGINGFACE_API_KEY, HUGGINGFACE_MODEL, HUGGINGFACE_API_BASE, HUGGINGFACE_API_TIMEOUT
    
    if st is None:
        return
    
    # Suppress Streamlit warnings about missing secrets.toml
    import sys
    import io
    from pathlib import Path
    
    # Check if secrets file exists before trying to access st.secrets
    user_config_path = Path.home() / ".streamlit" / "secrets.toml"
    workspace_config_path = Path.cwd() / ".streamlit" / "secrets.toml"
    
    if not user_config_path.exists() and not workspace_config_path.exists():
        return  # No secrets file, skip loading
    
    # Suppress stderr during secrets access to hide warnings
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    try:
        OPENAI_API_KEY = OPENAI_API_KEY or get_st_secret("api_key", "", section="openai") or get_st_secret("OPENAI_API_KEY", "")
        OPENAI_MODEL = OPENAI_MODEL or get_st_secret("model", "gpt-4o-mini", section="openai") or get_st_secret("OPENAI_MODEL", "gpt-4o-mini")
        OPENAI_API_BASE = OPENAI_API_BASE or get_st_secret("api_base", "https://api.openai.com/v1", section="openai").rstrip("/") or get_st_secret("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
        OPENAI_API_TIMEOUT = int(get_st_secret("api_timeout", str(OPENAI_API_TIMEOUT), section="openai") or OPENAI_API_TIMEOUT)

        HUGGINGFACE_API_KEY = HUGGINGFACE_API_KEY or get_st_secret("api_key", "", section="huggingface") or get_st_secret("HUGGINGFACE_API_KEY", "")
        HUGGINGFACE_MODEL = HUGGINGFACE_MODEL or get_st_secret("model", "google/flan-t5-large", section="huggingface") or get_st_secret("HUGGINGFACE_MODEL", "google/flan-t5-large")
        HUGGINGFACE_API_BASE = HUGGINGFACE_API_BASE or get_st_secret("api_base", "https://api-inference.huggingface.co", section="huggingface").rstrip("/") or get_st_secret("HUGGINGFACE_API_BASE", "https://api-inference.huggingface.co").rstrip("/")
        HUGGINGFACE_API_TIMEOUT = int(get_st_secret("api_timeout", str(HUGGINGFACE_API_TIMEOUT), section="huggingface") or HUGGINGFACE_API_TIMEOUT)
    except Exception:
        pass  # If secrets loading fails, fall back to environment variables
    finally:
        sys.stderr = old_stderr

# ---------------------------------
# Load template configuration
# ---------------------------------
with open(
    "templates/canonical_template.json",
    "r"
) as file:

    CANONICAL_TEMPLATE = json.load(
        file
    )

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedding_model = None


def _json_serializable_fallback(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if pd.isna(obj):
        return None
    return str(obj)


def _normalize_template_columns(template_columns):
    if template_columns is None:
        return CANONICAL_TEMPLATE
    if isinstance(template_columns, list):
        return {col: col for col in template_columns}
    if isinstance(template_columns, dict):
        return template_columns
    raise ValueError("template_columns must be a dict or list.")


def _parse_sample_rows(sample_rows):
    if sample_rows is None:
        return []
    if isinstance(sample_rows, str):
        try:
            return json.loads(sample_rows)
        except Exception:
            return []
    if isinstance(sample_rows, list):
        return sample_rows
    return []


def _build_column_text(column_name, column_info, sample_values=None):
    semantic_name = ""
    transformations = ""

    if isinstance(column_info, dict):
        semantic_name = str(column_info.get("semantic_name", "")).strip()
        transformations = " ".join(column_info.get("transformation_reason", [])).strip()
    else:
        semantic_name = str(column_info).strip()

    parts = [str(column_name)]
    if semantic_name:
        parts.append(semantic_name)
    if transformations:
        parts.append(transformations)
    if sample_values:
        sample_text = ", ".join(str(v) for v in sample_values if v is not None and str(v).strip())
        if sample_text:
            parts.append(f"Sample values: {sample_text}")

    if len(parts) == 2:
        return ": ".join(parts)
    return " ".join(parts)


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is required for embedding-based semantic mapping.")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _compute_embeddings(texts):
    if not texts:
        return []
    model = _get_embedding_model()
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)


def _generate_embedding_matches(dataset_columns, template_columns, sample_rows=None):
    source_cols = list(dataset_columns.keys())
    target_cols = list(template_columns.keys())

    if not source_cols or not target_cols:
        return {}

    sample_rows = _parse_sample_rows(sample_rows)
    sample_values_by_col = {}
    for col in source_cols:
        values = []
        for row in sample_rows:
            if not isinstance(row, dict):
                continue
            value = row.get(col, None)
            if value is not None and not pd.isna(value):
                values.append(value)
            if len(values) >= 3:
                break
        sample_values_by_col[col] = values

    source_texts = [
        _build_column_text(col, dataset_columns[col], sample_values=sample_values_by_col.get(col))
        for col in source_cols
    ]
    target_texts = [
        _build_column_text(target, template_columns[target])
        if isinstance(template_columns[target], dict)
        else f"{target}: {template_columns[target]}"
        for target in target_cols
    ]

    source_embeddings = _compute_embeddings(source_texts)
    target_embeddings = _compute_embeddings(target_texts)
    similarity_matrix = cosine_similarity(source_embeddings, target_embeddings)

    matches = {}
    for idx, col in enumerate(source_cols):
        similarities = similarity_matrix[idx]
        sorted_indexes = similarities.argsort()[::-1]
        best_index = int(sorted_indexes[0])
        second_score = float(similarities[sorted_indexes[1]]) if len(similarities) > 1 else 0.0
        matches[col] = {
            "target": target_cols[best_index],
            "score": float(similarities[best_index]),
            "second_score": second_score,
            "candidates": [
                {"target": target_cols[i], "score": float(similarities[i])}
                for i in sorted_indexes[:3]
            ]
        }

    return matches


def _has_llm_credentials():
    return bool(OPENAI_API_KEY or HUGGINGFACE_API_KEY)


def _call_llm_api(prompt):
    if OPENAI_API_KEY:
        url = f"{OPENAI_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 1024
        }
        timeout = OPENAI_API_TIMEOUT

        print("\n[DEBUG] Sending request to OpenAI-compatible cloud LLM API... please wait...")
    elif HUGGINGFACE_API_KEY:
        url = f"{HUGGINGFACE_API_BASE}/models/{HUGGINGFACE_MODEL}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 1024, "temperature": 0.0},
            "options": {"wait_for_model": True}
        }
        timeout = HUGGINGFACE_API_TIMEOUT

        print("\n[DEBUG] Sending request to Hugging Face inference API... please wait...")
    else:
        raise ValueError("OPENAI_API_KEY or HUGGINGFACE_API_KEY environment variable is required for cloud LLM calls.")

    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    response_json = response.json()

    if isinstance(response_json, dict) and "choices" in response_json:
        return response_json["choices"][0]["message"]["content"].strip()
    if isinstance(response_json, dict) and "generated_text" in response_json:
        return response_json["generated_text"].strip()
    if isinstance(response_json, list) and response_json:
        first = response_json[0]
        if isinstance(first, dict) and "generated_text" in first:
            return first["generated_text"].strip()
    return response.text.strip()


def _llm_assisted_mapping(ambiguous_columns, template_columns, sample_rows):
    sample_rows = _parse_sample_rows(sample_rows)
    template_schema = {
        target: template_columns[target]
        if not isinstance(template_columns[target], dict)
        else template_columns[target].get("semantic_name", str(template_columns[target]))
        for target in template_columns
    }

    source_description = {
        col: _build_column_text(col, ambiguous_columns[col])
        for col in ambiguous_columns
    }

    prompt = f"""
You are an expert data harmonization assistant.

Target canonical schema fields:
{json.dumps(template_schema, indent=2)}

Source columns to map with semantic hints:
{json.dumps(source_description, indent=2)}

Representative sample records:
{json.dumps(sample_rows[:10], indent=2, default=_json_serializable_fallback)}

CRITICAL INSTRUCTIONS:
1. For each source column above, select the best matching target column key from the canonical schema.
2. If no target is appropriate, return "UNKNOWN".
3. Return only a flat JSON object with source keys and target values.
4. Do not include markdown, commentary, or extra text.
"""

    llm_output = _call_llm_api(prompt)
    parsed_mapping = json.loads(llm_output)

    result = {}
    for source_col, target_col in parsed_mapping.items():
        if isinstance(target_col, str) and (target_col in template_columns or target_col == "UNKNOWN"):
            result[source_col] = target_col
        else:
            result[source_col] = "UNKNOWN"
    return result


# ---------------------------------
# Function for semantic mapping with embeddings + LLM fallback
# ---------------------------------
def semantic_column_mapping(
    dataset_columns,
    template_columns=None,
    sample_rows=None
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

    template_columns = _normalize_template_columns(template_columns)
    mapping_results = {}
    mapping_reasoning = {}
    columns_to_evaluate = {}

    for dataset_col, description in dataset_columns.items():
        if dataset_col in IGNORE_COLUMNS:
            mapping_results[dataset_col] = "UNKNOWN"
            mapping_reasoning[dataset_col] = "Ignored column"
            continue

        if dataset_col in RULE_BASED_MAPPING:
            mapping_results[dataset_col] = RULE_BASED_MAPPING[dataset_col]
            mapping_reasoning[dataset_col] = "Matched via Rule-Based System"
            continue

        columns_to_evaluate[dataset_col] = description

    if not columns_to_evaluate:
        return {"mapping": mapping_results, "reasoning": mapping_reasoning}

    embedding_matches = _generate_embedding_matches(columns_to_evaluate, template_columns, sample_rows=sample_rows)

    ambiguous_columns = {}
    for dataset_col, match_info in embedding_matches.items():
        best_target = match_info["target"]
        best_score = match_info["score"]
        second_score = match_info["second_score"]
        confidence_delta = best_score - second_score

        if best_score >= 0.60 and confidence_delta >= 0.08:
            mapping_results[dataset_col] = best_target
            mapping_reasoning[dataset_col] = f"Embedding match ({best_score:.2f})"
            continue

        if best_score >= 0.48 and confidence_delta >= 0.08:
            mapping_results[dataset_col] = best_target
            mapping_reasoning[dataset_col] = f"Embedding match (medium confidence {best_score:.2f})"
            continue

        ambiguous_columns[dataset_col] = columns_to_evaluate[dataset_col]

    if ambiguous_columns and _has_llm_credentials():
        try:
            llm_mapping = _llm_assisted_mapping(ambiguous_columns, template_columns, sample_rows)
            for dataset_col, target_col in llm_mapping.items():
                if target_col == "UNKNOWN":
                    mapping_results[dataset_col] = "UNKNOWN"
                    mapping_reasoning[dataset_col] = "LLM-assisted mapping (no suitable target)"
                else:
                    mapping_results[dataset_col] = target_col
                    mapping_reasoning[dataset_col] = f"LLM-assisted mapping ({target_col})"
            ambiguous_columns = {
                col: desc for col, desc in ambiguous_columns.items()
                if col not in llm_mapping
            }
        except Exception as e:
            print(f"\n[WARNING] Cloud LLM call failed: {e}. Falling back to embedding matches.")

    for dataset_col, description in ambiguous_columns.items():
        match_info = embedding_matches.get(dataset_col, {})
        best_target = match_info.get("target", "UNKNOWN")
        best_score = match_info.get("score", 0.0)

        if best_score >= 0.50:
            mapping_results[dataset_col] = best_target
            mapping_reasoning[dataset_col] = f"Fallback embedding match ({best_score:.2f})"
        else:
            mapping_results[dataset_col] = "UNKNOWN"
            mapping_reasoning[dataset_col] = "Low confidence embedding mapping"

    return {"mapping": mapping_results, "reasoning": mapping_reasoning}


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
    all_reasonings = {}

    for (
        dataset_name,
        dataset_info
    ) in datasets.items():

        result = semantic_column_mapping(
            dataset_info["schema"],
            template_columns,
            dataset_info["sample_rows"]
        )

        all_mappings[dataset_name] = result["mapping"]

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