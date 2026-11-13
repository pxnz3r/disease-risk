"""
app.py - the heart disease risk demo. Run it with:

    streamlit run app.py

Tabs:
    Overview   what the project is, how the two models decide, and its limits,
    Assess     fill in a patient (or start from a real test patient) and see
               each model's verdict and why,
    Rules      every rule the Decision Tree learned,
    Results    the saved tables and figures from main.py.
It needs the saved models, so run `python main.py` once first.

Educational only: not a medical tool.
"""

import os

import pandas as pd
import streamlit as st

from disease_risk.explain import patient_evidence
from disease_risk.report import FOLDER, results_sections
from disease_risk.spec import HEART_SPEC
from pxlab.app import (
    input_form,
    probability_bar,
    setup_page,
    show_figure,
    show_markdown_file,
    show_results_tabs,
    signed_bars,
)
from pxlab.common import MODELS_FOLDER, OUTPUTS_FOLDER
from pxlab.tabular.explain import decision_path
from pxlab.tabular.train import load_models, models_are_saved

MODEL_FOLDER = os.path.join(MODELS_FOLDER, FOLDER)
TYPICAL = "Typical patient"
TEST_EXAMPLES = 15
NOT_A_TOOL = "Educational demo built on 1980s research data. It can't diagnose anyone; see a doctor about symptoms."


@st.cache_resource
def load_everything():
    """
    Load the saved models and the test set (cached, so this happens once).

    Returns:
        (model_info, models, test table)
    """
    model_info, models = load_models(MODEL_FOLDER)
    test = pd.read_csv(os.path.join(MODEL_FOLDER, "test.csv"))
    return model_info, models, test


def show_assess_page(model_info, models, test):
    """
    The Assess tab: the patient on the left, the verdict and the reasons
    on the right.

    Inputs:
        model_info, models: from load_models().
        test: the saved test table.
    Returns:
        Nothing.
    """
    spec = HEART_SPEC
    inputs = list(spec["numeric"]) + list(spec["categorical"])
    left, right = st.columns([3, 2], gap="large")
    with left:
        picker, model_box = st.columns(2)
        test_options = [
            f"Test patient {number + 1} ({test['diagnosis'].iloc[number]})"
            for number in range(min(TEST_EXAMPLES, len(test)))
        ]
        start = picker.selectbox(
            "Start from",
            [TYPICAL, *test_options],
            help="The typical patient has the training medians and most common answers. "
            "Test patients are real records the models never saw.",
        )
        model_name = model_box.selectbox("Model", list(models), index=list(models).index("Naive Bayes"))
        if start == TYPICAL:
            start_values = model_info["default_values"]
        else:
            start_values = test.iloc[test_options.index(start)][inputs].to_dict()
        patient = input_form(spec, model_info, start_values, key_prefix=f"{start}-")

    pipeline = models[model_name]
    disease_column = list(pipeline.classes_).index("heart disease")
    chance = float(pipeline.predict_proba(patient)[0, disease_column])
    with right:
        st.subheader("Heart disease likely" if chance >= 0.5 else "Heart disease unlikely", anchor=False)
        st.markdown(f"Model's chance of heart disease **{chance:.0%}**")
        probability_bar(chance, threshold=0.5)
        st.caption(NOT_A_TOOL)
        if model_name == "Naive Bayes":
            st.subheader("What pushed it", anchor=False)
            st.caption("Evidence per input: right points to heart disease, left away from it.")
            signed_bars(patient_evidence(pipeline, patient, spec).head(8))
        elif model_name == "Decision Tree":
            st.subheader("The questions the tree asked", anchor=False)
            steps = decision_path(pipeline, patient, spec)
            st.markdown("\n".join(f"{number}. {step}" for number, step in enumerate(steps, start=1)))
        else:
            st.caption("Pick Naive Bayes or the Decision Tree to see why.")


def show_rules_page(model_info):
    """
    The Rules tab: the top of the tree and the full rule list.

    Input:
        model_info: from load_models().
    Returns:
        Nothing.
    """
    best = model_info["best_params"]["Decision Tree"]
    st.markdown(
        f"Cross-validation chose a tree of depth {best['max_depth']} with at least {best['min_samples_leaf']} "
        f"training patients per leaf, giving {model_info['tree_leaves']} leaves. Read each rule from the top: "
        "every line is a question, and indented lines apply only when it is true."
    )
    show_figure(f"{FOLDER}/decision_tree.png")
    with open(os.path.join(OUTPUTS_FOLDER, FOLDER, "tree_rules.txt"), encoding="utf-8") as file:
        st.code(file.read(), language=None)


def main():
    """
    Build the page.

    Returns:
        Nothing.
    """
    setup_page("Heart disease risk")
    if not models_are_saved(MODEL_FOLDER):
        st.error("No saved models yet. Run `python main.py` first.")
        st.stop()
    model_info, models, test = load_everything()

    overview, assess, rules, results = st.tabs(["Overview", "Assess", "Rules", "Results"])
    with overview:
        show_markdown_file("app_overview.md")
    with assess:
        show_assess_page(model_info, models, test)
    with rules:
        show_rules_page(model_info)
    with results:
        show_results_tabs(results_sections())


main()
