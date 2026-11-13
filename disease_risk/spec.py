"""
spec.py - the heart disease dataset and the models trained on it.

The pxlab engine reads this dictionary: which column to predict, which
columns are inputs, readable names, and the models with the settings that
grid search tries.

The brief allows a Decision Tree or Naive Bayes; both are trained and
compared, because they fail in different ways.
"""

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

from pxlab.common import RANDOM_STATE

# Tree depths tried by grid search.
DEPTHS = [2, 3, 4, 5, 6]

HEART_SPEC = {
    "name": "Heart disease (Cleveland)",
    "folder": "heart",
    "task": "classification",
    "target": "diagnosis",
    "positive_class": "heart disease",
    "numeric": ["age", "resting_blood_pressure", "cholesterol", "max_heart_rate", "st_depression", "major_vessels"],
    "categorical": [
        "sex",
        "chest_pain",
        "high_fasting_sugar",
        "resting_ecg",
        "exercise_angina",
        "st_slope",
        "thallium_scan",
    ],
    "whole_numbers": ["age", "resting_blood_pressure", "cholesterol", "max_heart_rate", "major_vessels"],
    "labels": {
        "age": "Age",
        "sex": "Sex",
        "chest_pain": "Chest pain type",
        "resting_blood_pressure": "Resting blood pressure (mm Hg)",
        "cholesterol": "Cholesterol (mg/dl)",
        "high_fasting_sugar": "Fasting blood sugar",
        "resting_ecg": "Resting ECG",
        "max_heart_rate": "Highest heart rate in exercise test",
        "exercise_angina": "Chest pain during exercise",
        "st_depression": "ST depression in exercise",
        "st_slope": "ST slope at peak exercise",
        "major_vessels": "Major vessels seen in fluoroscopy (0 to 3)",
        "thallium_scan": "Thallium heart scan",
        "diagnosis": "Diagnosis",
    },
    "help": {
        "chest_pain": "Typical angina is chest pain brought on by effort and eased by rest.",
        "st_depression": "How far the ST segment of the ECG drops during exercise compared with rest, in mm. "
        "A larger drop suggests the heart muscle is short of blood under load.",
        "st_slope": "The direction of the ST segment at peak exercise.",
        "major_vessels": "How many of the three main heart arteries show up in an X-ray dye test.",
        "thallium_scan": "A scan of blood flow to the heart muscle. A fixed defect is a scar; "
        "a reversible defect is an area short of blood only under stress.",
    },
    "test_size": 0.25,
    "scoring": "roc_auc",
    "models": {
        "Decision Tree": {
            "estimator": DecisionTreeClassifier(random_state=RANDOM_STATE),
            "grid": {"max_depth": DEPTHS, "min_samples_leaf": [5, 10, 20], "class_weight": [None, "balanced"]},
            "scale": False,
            "role": "Main",
        },
        "Naive Bayes": {
            # Gaussian Naive Bayes: a bell curve per input and class. The
            # smoothing adds a little spread so a 0/1 column that never varies
            # within one class doesn't make the other value impossible.
            "estimator": GaussianNB(),
            "grid": {"var_smoothing": [1e-9, 1e-3, 1e-2, 1e-1]},
            "scale": True,
            "role": "Main",
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=1),
            "grid": {"min_samples_leaf": [1, 5, 10]},
            "scale": False,
            "role": "Benchmark beyond the course",
        },
        "Always healthy": {
            "estimator": DummyClassifier(strategy="most_frequent"),
            "grid": {},
            "scale": False,
            "role": "Baseline",
        },
    },
}
