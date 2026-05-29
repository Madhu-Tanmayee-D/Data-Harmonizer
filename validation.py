import pandas as pd
import json


def validate_dataset(
    harmonized_dataset,
    template_path="templates/canonical_template.json"
):

    # -----------------------------
    # Missing values
    # -----------------------------
    missing_values = (
        harmonized_dataset
        .isnull()
        .sum()
    )

    # -----------------------------
    # Duplicate rows
    # -----------------------------
    duplicates = (
        harmonized_dataset
        .duplicated()
        .sum()
    )

    # -----------------------------
    # Schema compliance
    # -----------------------------
    with open(
        template_path,
        "r"
    ) as file:

        template_columns = json.load(
            file
        )

    expected_columns = list(
        template_columns.keys()
    )

    actual_columns = list(
        harmonized_dataset.columns
    )

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    # -----------------------------
    # Save validation report
    # -----------------------------
    validation_report = pd.DataFrame({
        "column":
            harmonized_dataset.columns,

        "missing_values":
            harmonized_dataset
            .isnull()
            .sum()
            .values,

        "data_type":
            harmonized_dataset
            .dtypes
            .astype(str)
            .values
    })

    validation_report.loc[
        len(validation_report)
    ] = [
        "duplicate_rows",
        duplicates,
        "-"
    ]

    validation_report.to_csv(
        "outputs/validation_report.csv",
        index=False
    )

    return validation_report