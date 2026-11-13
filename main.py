"""
main.py - run the whole heart disease study with one command:

    python main.py

It:
    1. downloads (once) and checks the Cleveland heart disease data,
    2. keeps 25% of the patients back as a test set,
    3. tunes a Decision Tree and Naive Bayes with 5-fold cross-validation,
       plus a Random Forest benchmark and an "always healthy" baseline,
    4. scores them on the test set and draws confusion matrices and ROC
       curves,
    5. writes out the tree's rules and draws its top levels,
    6. shows how the cut-off trades missed patients for false alarms,
    7. scores the Cleveland models on three other hospitals,
    8. measures which inputs matter and lists the mistakes,
    9. saves the models for the app and writes docs/results.md.
Figures and tables go to outputs/heart/, models to models/heart/.
"""

import os

import pandas as pd

from disease_risk.data import HOSPITAL_FILES, TRAINING_HOSPITAL, load_hospital
from disease_risk.explain import cutoff_table, hospital_table
from disease_risk.report import FOLDER, results_sections
from disease_risk.spec import HEART_SPEC
from pxlab.common import MODELS_FOLDER, save_table, set_plot_style, write_results_doc
from pxlab.tabular.data import (
    check_columns,
    feature_columns,
    input_summary,
    label_for,
    plot_correlations,
    plot_target,
    quality_report,
    split_data,
)
from pxlab.tabular.evaluate import (
    comparison_table,
    plot_confusion_matrices,
    plot_roc_curves,
    test_scores,
    wrong_predictions,
)
from pxlab.tabular.explain import (
    permutation_importance_table,
    plot_permutation_importance,
    plot_tree_top,
    tree_rules,
)
from pxlab.tabular.train import best_model_name, save_models, train_models


def missing_by_hospital(hospitals, spec):
    """
    The share of missing values per input at each hospital.

    Inputs:
        hospitals: dictionary hospital name -> DataFrame.
        spec: the project SPEC.
    Returns:
        A DataFrame: one row per input, one column per hospital.
    """
    table = pd.DataFrame({name: data[feature_columns(spec)].isna().mean() for name, data in hospitals.items()})
    table.index = [label_for(spec, column) for column in table.index]
    return table.round(2)


def main():
    """
    The full study.

    Returns:
        Nothing.
    """
    spec = HEART_SPEC
    set_plot_style()
    data = load_hospital(TRAINING_HOSPITAL)
    check_columns(data, spec)
    quality_report(data, spec, f"{FOLDER}/data_quality.csv")
    plot_target(data, spec, f"{FOLDER}/target.png")
    plot_correlations(data, spec, f"{FOLDER}/correlations.png")

    train_features, test_features, train_target, test_target = split_data(data, spec)
    model_folder = os.path.join(MODELS_FOLDER, FOLDER)
    os.makedirs(model_folder, exist_ok=True)
    test_features.assign(diagnosis=test_target).to_csv(os.path.join(model_folder, "test.csv"), index=False)

    print("Tuning with 5-fold cross-validation:")
    results = train_models(spec, train_features, train_target)
    table = comparison_table(results, test_features, test_target, spec, f"{FOLDER}/model_comparison.csv")
    print(table.to_string(index=False))
    plot_confusion_matrices(results, test_features, test_target, f"{FOLDER}/confusion_matrices.png")
    plot_roc_curves(results, test_features, test_target, spec["positive_class"], f"{FOLDER}/roc_curves.png")

    tree = results["Decision Tree"]["pipeline"]
    bayes = results["Naive Bayes"]["pipeline"]
    tree_rules(tree, spec, max_depth=20, filename=f"{FOLDER}/tree_rules.txt")
    plot_tree_top(tree, spec, depth=3, filename=f"{FOLDER}/decision_tree.png")
    save_table(wrong_predictions(bayes, test_features, test_target, spec), f"{FOLDER}/wrong_predictions.csv")
    for name, pipeline in [("naive_bayes", bayes), ("decision_tree", tree)]:
        cutoffs = cutoff_table(pipeline, test_features, test_target, spec, filename=f"{FOLDER}/cutoffs_{name}.csv")
        print(f"  Cut-offs, {name}:\n{cutoffs.to_string(index=False)}")

    hospitals = {name: load_hospital(name) for name in HOSPITAL_FILES}
    save_table(missing_by_hospital(hospitals, spec), f"{FOLDER}/missing_by_hospital.csv", index=True)
    others = {name: frame for name, frame in hospitals.items() if name != TRAINING_HOSPITAL}
    elsewhere = hospital_table(results, others, spec, f"{FOLDER}/other_hospitals.csv")
    print(elsewhere.to_string(index=False))

    explained = {name: result for name, result in results.items() if result["role"] != "Baseline"}
    importance = permutation_importance_table(
        explained, test_features, test_target, spec, filename=f"{FOLDER}/permutation_importance.csv"
    )
    plot_permutation_importance(importance, filename=f"{FOLDER}/permutation_importance.png")

    model_info = {
        "dataset": "UCI Heart Disease, Cleveland",
        "classes": ["heart disease", "no disease"],
        "best_model": best_model_name(results),
        "test_scores": {
            name: test_scores(r["pipeline"], test_features, test_target, spec) for name, r in results.items()
        },
        "cv_scores": {name: r["cv_score"] for name, r in results.items()},
        "tree_leaves": int(tree.named_steps["model"].get_n_leaves()),
        "tree_depth": int(tree.named_steps["model"].get_depth()),
    }
    model_info.update(input_summary(train_features, spec))
    save_models(results, model_info, folder=model_folder)

    write_results_doc(
        "Results",
        "Produced by `python main.py`. The test set is 25% of the Cleveland patients, stratified, and was not "
        f"used for tuning or model choice. The full rules of the tree are in `outputs/{FOLDER}/tree_rules.txt`. "
        "Educational only, not a medical tool.\n\n"
        f"![Top of the Decision Tree](../outputs/figures/{FOLDER}/decision_tree.png)",
        results_sections(),
    )
    print("  Done. Run: streamlit run app.py")


if __name__ == "__main__":
    main()
