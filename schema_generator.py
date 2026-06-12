from column_semantics import (
    generate_column_description
)

def generate_schema(columns, bypass_words=None):
    """
    Generates a schema dictionary where each key is the raw column name
    and the value is a dictionary containing the semantic analysis.
    """
    schema = {}

    for column in columns:
        # Now receives the full dictionary: 
        # {'semantic_name': ..., 'transformation_reason': [...]}
        semantic_info = generate_column_description(
            column,
            bypass_words=bypass_words
        )
        
        schema[column] = semantic_info

    return schema