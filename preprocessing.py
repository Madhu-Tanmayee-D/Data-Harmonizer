import pandas as pd


# ---------------------------------
# Function to clean column names
# ---------------------------------
def clean_column_names(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


# -------------------------------
# Generic dataset preprocessing
# -------------------------------
def process_dataset(
    dataframe
):
    # Create an explicit deep copy to eliminate any SettingWithCopyWarning
    dataframe = dataframe.copy()

    # -------------------------------
    # Clean column names
    # -------------------------------
    dataframe = clean_column_names(
        dataframe
    )

    # -------------------------------
    # Remove duplicates
    # -------------------------------
    dataframe = (
        dataframe
        .drop_duplicates()
    )

    # -------------------------------
    # Generic numeric cleanup
    # -------------------------------
    for column in dataframe.columns:

        # Convert numeric-looking columns without using deprecated arguments
        try:
            converted = pd.to_numeric(dataframe[column], errors="raise")
            dataframe[column] = converted
        except Exception:
            pass

    # -------------------------------
    # Generic datetime conversion
    # -------------------------------
    for column in dataframe.columns:

        if any(
            keyword in column.lower()
            for keyword in [
                "date",
                "time",
                "datetime",
                "timestamp"
            ]
        ):

            dataframe[column] = pd.to_datetime(
                dataframe[column],
                errors="coerce"
            )

    return dataframe