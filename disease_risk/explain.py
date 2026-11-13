"""
explain.py - how the heart disease models reach a verdict, beyond what
pxlab already provides (tree rules and decision paths).

    patient_evidence: for Naive Bayes, how much each input pushed one
        patient towards heart disease or away from it.
    cutoff_table: what happens to missed patients and false alarms when
        the cut-off for "heart disease" moves.
    hospital_table: how the models trained in Cleveland score at the
        other three hospitals.
"""

import numpy as np
import pandas as pd

from pxlab.common import save_table
from pxlab.tabular.data import label_for
from pxlab.tabular.evaluate import test_scores


def patient_evidence(pipeline, patient, spec):
    """
    Naive Bayes multiplies one chance per input. On a log scale that is a
    sum, so each input's share of the verdict can be read off:

        evidence = log P(value | heart disease) - log P(value | no disease)

    Positive pushes towards heart disease, negative away from it. A
    category column (one-hot encoded into several 0/1 columns) gets the sum
    of its columns.

    Inputs:
        pipeline: the fitted Naive Bayes pipeline.
        patient: a one-row DataFrame with the raw input columns.
        spec: the project SPEC.
    Returns:
        A Series: readable input name -> evidence, largest effect first.
    """
    model = pipeline.named_steps["model"]
    values = pipeline.named_steps["preprocess"].transform(patient)[0]
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    positive = list(model.classes_).index(spec["positive_class"])
    negative = 1 - positive
    # Log of the bell-curve height at this value, for each class.
    log_density = -0.5 * np.log(2 * np.pi * model.var_) - (values - model.theta_) ** 2 / (2 * model.var_)
    evidence_per_column = log_density[positive] - log_density[negative]

    evidence = {}
    for name, value in zip(names, evidence_per_column):
        column = name
        for category_column in spec["categorical"]:
            if name.startswith(category_column + "_"):
                column = category_column
        label = label_for(spec, column)
        evidence[label] = evidence.get(label, 0.0) + value
    evidence = pd.Series(evidence)
    return evidence.reindex(evidence.abs().sort_values(ascending=False).index)


def cutoff_table(pipeline, features, target, spec, cutoffs=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7), filename=None):
    """
    Missed patients and false alarms at different cut-offs.

    A model gives a chance of heart disease; the cut-off turns it into a
    yes or no. Lowering the cut-off flags more patients: fewer sick
    patients are missed, but more healthy ones are sent for tests.

    Inputs:
        pipeline: a fitted classifier pipeline.
        features, target: the data to score on.
        spec: the project SPEC.
        cutoffs: the cut-offs to try.
        filename: the CSV file inside outputs/, or None to not save.
    Returns:
        A DataFrame: cut-off, flagged, missed, false alarms, recall, precision.
    """
    column = list(pipeline.classes_).index(spec["positive_class"])
    chances = pipeline.predict_proba(features)[:, column]
    sick = (target == spec["positive_class"]).to_numpy()
    rows = []
    for cutoff in cutoffs:
        flagged = chances >= cutoff
        caught = int((flagged & sick).sum())
        rows.append(
            {
                "Cut-off": cutoff,
                "Flagged": int(flagged.sum()),
                "Missed (sick, not flagged)": int((~flagged & sick).sum()),
                "False alarms (healthy, flagged)": int((flagged & ~sick).sum()),
                "Recall": round(caught / max(sick.sum(), 1), 3),
                "Precision": round(caught / max(flagged.sum(), 1), 3),
            }
        )
    table = pd.DataFrame(rows)
    if filename:
        save_table(table, filename)
    return table


def hospital_table(results, hospitals, spec, filename):
    """
    Scores of every trained model on patients from other hospitals.

    Inputs:
        results: from train_models() (trained on Cleveland only).
        hospitals: dictionary hospital name -> DataFrame from load_hospital().
        spec: the project SPEC.
        filename: the CSV file inside outputs/.
    Returns:
        A DataFrame: one row per hospital and model.
    """
    rows = []
    inputs = list(spec["numeric"]) + list(spec["categorical"])
    for hospital, data in hospitals.items():
        target = data[spec["target"]]
        for model_name, result in results.items():
            scores = test_scores(result["pipeline"], data[inputs], target, spec)
            rows.append(
                {
                    "Hospital": hospital,
                    "Patients": len(data),
                    "With heart disease": round(float((target == spec["positive_class"]).mean()), 3),
                    "Model": model_name,
                    "Accuracy": scores["Accuracy"],
                    "Recall": scores["Recall"],
                    "ROC-AUC": scores.get("ROC-AUC", np.nan),
                }
            )
    table = pd.DataFrame(rows).round(3)
    save_table(table, filename)
    return table
