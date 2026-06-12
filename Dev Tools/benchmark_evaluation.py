from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

import matplotlib.pyplot as plt
import seaborn as sns


def evaluate_mapping(
    predicted_mapping,
    ground_truth_mapping,
    dataset_name="dataset",
    ignore_list=None
):
    if ignore_list is None:
        ignore_list = []

    y_true = []
    y_pred = []

    for column in ground_truth_mapping:
        # Skip columns that were purposefully dropped by the pipeline
        # to ensure evaluation metrics remain accurate and fair.
        if column in ignore_list:
            continue

        y_true.append(
            ground_truth_mapping[column]
        )

        y_pred.append(
            predicted_mapping.get(
                column,
                "UNKNOWN"
            )
        )

    # -----------------------
    # Metrics
    # -----------------------

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    print(
        f"\n{dataset_name.upper()}"
    )

    print(
        f"Accuracy: "
        f"{accuracy:.4f}"
    )

    print(
        f"Precision: "
        f"{precision:.4f}"
    )

    print(
        f"Recall: "
        f"{recall:.4f}"
    )

    print(
        f"F1 Score: "
        f"{f1:.4f}"
    )

    print(
        "\nClassification Report:\n"
    )

    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    # -----------------------
    # Confusion Matrix
    # -----------------------

    labels = sorted(
        list(
            set(
                y_true
                +
                y_pred
            )
        )
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    plt.figure(
        figsize=(10, 8)
    )

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=labels,
        yticklabels=labels
    )

    plt.xlabel(
        "Predicted"
    )

    plt.ylabel(
        "Actual"
    )

    plt.title(
        f"{dataset_name} "
        f"Confusion Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        f"{dataset_name}_confusion_matrix.png"
    )

    plt.close()