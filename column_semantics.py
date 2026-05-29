# ---------------------------------
# Generate semantic meaning
# from column names
# ---------------------------------

def generate_column_description(
    column_name,
    bypass_words=None
):
    if bypass_words is None:
        bypass_words = []

    # Clean snake_case and standardize case
    column_name_clean = (
        column_name
        .lower()
        .replace(
            "_",
            " "
        )
    )

    # If the cleaned column name or the raw column name matches a rule-based key,
    # we return it as-is to preserve exact lookups in rule_based_mapping.json.
    if column_name in bypass_words or column_name_clean in bypass_words:
        return column_name_clean

    COMMON_EXPANSIONS = {
        "id":
        "identifier",

        "amt":
        "amount",

        "qty":
        "quantity",

        "txn":
        "transaction",

        "dt":
        "date",

        "dob":
        "date of birth",

        "addr":
        "address",

        "loc":
        "location",

        "cust":
        "customer",

        "prod":
        "product"
    }

    words = []

    for word in (
        column_name_clean.split()
    ):
        words.append(
            COMMON_EXPANSIONS.get(
                word,
                word
            )
        )

    return " ".join(
        words
    )