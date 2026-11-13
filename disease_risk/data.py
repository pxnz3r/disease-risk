"""
data.py - the UCI Heart Disease data (Janosi, Steinbrunn, Pfisterer and
Detrano, 1988; UCI Machine Learning Repository, CC BY 4.0). Downloaded
once into data/.

Patients referred for a heart X-ray (angiography) at four hospitals. The
diagnosis is whether any main artery was narrowed by more than half. The
models learn from the Cleveland Clinic patients; the other three hospitals
are kept apart to test whether what was learned in Cleveland carries over.
"""

import os
import zipfile

import numpy as np
import pandas as pd

from pxlab.common import DATA_FOLDER, download_once

HEART_URL = "https://archive.ics.uci.edu/static/public/45/heart+disease.zip"

# The 14 columns of the processed files, in order.
COLUMNS = [
    "age",
    "sex",
    "chest_pain",
    "resting_blood_pressure",
    "cholesterol",
    "high_fasting_sugar",
    "resting_ecg",
    "max_heart_rate",
    "exercise_angina",
    "st_depression",
    "st_slope",
    "major_vessels",
    "thallium_scan",
    "narrowing",
]

HOSPITAL_FILES = {
    "Cleveland Clinic (US)": "processed.cleveland.data",
    "Hungarian Institute of Cardiology (Budapest)": "processed.hungarian.data",
    "University Hospitals (Zurich and Basel)": "processed.switzerland.data",
    "VA Medical Center (Long Beach, US)": "processed.va.data",
}
TRAINING_HOSPITAL = "Cleveland Clinic (US)"

# The original number codes made readable for the app's drop-downs.
READABLE_VALUES = {
    "sex": {1: "Male", 0: "Female"},
    "chest_pain": {1: "Typical angina", 2: "Atypical angina", 3: "Non-anginal pain", 4: "No chest pain"},
    "high_fasting_sugar": {1: "Above 120 mg/dl", 0: "120 mg/dl or below"},
    "resting_ecg": {0: "Normal", 1: "ST-T wave abnormality", 2: "Enlarged left ventricle"},
    "exercise_angina": {1: "Yes", 0: "No"},
    "st_slope": {1: "Rising", 2: "Flat", 3: "Falling"},
    "thallium_scan": {3: "Normal", 6: "Fixed defect", 7: "Reversible defect"},
}


def load_hospital(hospital=TRAINING_HOSPITAL):
    """
    One hospital's patients with readable values and the diagnosis column.

    Missing values are "?" in the files; a cholesterol or blood pressure of
    0 is also a missing measurement, not a real reading.

    Input:
        hospital: a key of HOSPITAL_FILES.
    Returns:
        A DataFrame with the 13 inputs and "diagnosis" (heart disease or
        no disease).
    """
    path = download_once(HEART_URL, os.path.join(DATA_FOLDER, "heart_disease.zip"))
    with zipfile.ZipFile(path) as archive:
        frame = pd.read_csv(archive.open(HOSPITAL_FILES[hospital]), header=None, names=COLUMNS, na_values="?")
    frame[["cholesterol", "resting_blood_pressure"]] = frame[["cholesterol", "resting_blood_pressure"]].replace(
        0, np.nan
    )
    for column, mapping in READABLE_VALUES.items():
        frame[column] = frame[column].map(mapping)
    # 0 means no artery narrowed by more than half; 1 to 4 means at least one.
    frame["diagnosis"] = np.where(frame.pop("narrowing") > 0, "heart disease", "no disease")
    return frame
