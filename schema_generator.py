from column_semantics import (
    generate_column_description
)


def generate_schema(columns, bypass_words=None):

    schema = {}

    for column in columns:

        # Passes the bypass_words list directly down to the description generator
        # to guarantee that exact lookup keys are preserved intact.
        schema[column] = (
            generate_column_description(
                column,
                bypass_words=bypass_words
            )
        )

    return schema