def generate_column_description(
    column_name,
    bypass_words=None
):
    if bypass_words is None:
        bypass_words = []

    # Clean snake_case and standardize case
    column_name_clean = column_name.lower().replace("_", " ")

    # If bypass logic hits, return without expansion
    if column_name in bypass_words or column_name_clean in bypass_words:
        return {
            "semantic_name": column_name_clean,
            "transformation_reason": [f"Used bypass rule for column: {column_name}"]
        }

    COMMON_EXPANSIONS = {
        "id": "identifier",
        "amt": "amount",
        "qty": "quantity",
        "txn": "transaction",
        "dt": "date",
        "dob": "date of birth",
        "addr": "address",
        "loc": "location",
        "cust": "customer",
        "prod": "product"
    }

    words = []
    reasoning = []

    for word in column_name_clean.split():
        if word in COMMON_EXPANSIONS:
            expanded = COMMON_EXPANSIONS[word]
            words.append(expanded)
            reasoning.append(f"Expanded abbreviation '{word}' to '{expanded}'")
        else:
            words.append(word)

    return {
        "semantic_name": " ".join(words),
        "transformation_reason": reasoning
    }