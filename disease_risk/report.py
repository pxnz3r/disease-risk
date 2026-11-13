"""
report.py - which saved tables and figures make up the results. The app's
Results tab and docs/results.md both read this list, so they always match.
"""

FOLDER = "heart"


def results_sections():
    """
    The results, grouped into sections.

    Returns:
        A list of (section name, items) for pxlab's show_results_tabs() and
        write_results_doc().
    """
    return [
        (
            "Models",
            [
                ("table", "Test-set scores (heart disease is the positive class)", f"{FOLDER}/model_comparison.csv"),
                ("figure", f"{FOLDER}/confusion_matrices.png"),
                ("figure", f"{FOLDER}/roc_curves.png"),
            ],
        ),
        (
            "Cut-off",
            [
                ("text", "Patients flagged, missed and falsely alarmed on the test set as the cut-off moves."),
                ("table", "Naive Bayes", f"{FOLDER}/cutoffs_naive_bayes.csv"),
                ("table", "Decision Tree", f"{FOLDER}/cutoffs_decision_tree.csv"),
            ],
        ),
        (
            "Other hospitals",
            [
                (
                    "text",
                    "Models trained on Cleveland patients, scored on patients from three other hospitals "
                    "they never saw. Several inputs are mostly missing at these hospitals.",
                ),
                ("table", "Scores per hospital", f"{FOLDER}/other_hospitals.csv"),
                ("table", "Share of missing values per hospital", f"{FOLDER}/missing_by_hospital.csv"),
            ],
        ),
        (
            "Which inputs matter",
            [
                ("figure", f"{FOLDER}/permutation_importance.png"),
                (
                    "table",
                    "Permutation importance (drop in ROC-AUC when the input is shuffled)",
                    f"{FOLDER}/permutation_importance.csv",
                ),
            ],
        ),
        ("Mistakes", [("table", "Test patients Naive Bayes got wrong", f"{FOLDER}/wrong_predictions.csv")]),
        (
            "Data",
            [
                ("table", "Data quality", f"{FOLDER}/data_quality.csv"),
                ("figure", f"{FOLDER}/target.png"),
                ("figure", f"{FOLDER}/correlations.png"),
            ],
        ),
    ]
