# Methodology

## Question

From a patient's routine measurements, can a Decision Tree or Naive Bayes tell who has heart disease, and where does that stop being trustworthy?

## Data

UCI Heart Disease, the processed Cleveland file: 303 patients referred to the Cleveland Clinic for coronary angiography (a heart X-ray with dye), 139 (46%) with at least one main artery narrowed by more than 50%. That narrowing is the "heart disease" label.

| Group | Inputs |
| --- | --- |
| Patient | age, sex |
| Symptoms | chest pain type, chest pain during exercise |
| Routine tests | resting blood pressure, cholesterol, fasting blood sugar, resting ECG |
| Exercise test | highest heart rate, ST depression, ST slope |
| Specialist tests | major vessels seen in fluoroscopy, thallium heart scan |

Number codes are turned into readable values in `disease_risk/data.py`. Six values are missing in Cleveland; they are filled with the training median or most common value inside the pipeline. A cholesterol or blood pressure of 0 in the other hospitals' files means "not measured" and is treated as missing.

Sex is kept: heart disease rates differ between men and women, and leaving it out would hide that rather than remove it.

## Steps

1. **Checks**: missing values, duplicates, the diagnosis split and correlations.
2. **Split**: 75% training, 25% test, stratified.
3. **Models**, each in a scikit-learn Pipeline (fill gaps, one-hot encode categories):
   - Decision Tree, tuned over depth (2 to 6), minimum patients per leaf (5 to 20) and class weights.
   - Gaussian Naive Bayes on standardised inputs, tuned over the variance smoothing (1e-9 to 0.1).
   - Random Forest, 300 trees, a benchmark beyond the course.
   - Always healthy, the baseline.
4. **Tuning**: 5-fold stratified cross-validation scored by ROC-AUC.
5. **Test scores**: accuracy, balanced accuracy, precision, recall and F1 for heart disease, and ROC-AUC. Confusion matrices and ROC curves.
6. **Cut-offs**: missed patients and false alarms at cut-offs from 20% to 70%, for both main models.
7. **Other hospitals**: the Cleveland-trained models scored on all patients from Budapest, Zurich and Basel, and Long Beach, with the share of missing values per input at each hospital.
8. **Explanations**: the tree's full rules and its top three levels; for Naive Bayes, per-patient evidence (the log ratio of each input's chance under heart disease and under no disease); permutation importance on the test set, 10 shuffles per input.
9. **In-depth analysis** (`pxlab.tabular.study`): 1,000-round bootstrap 95% intervals for the headline test scores, next to a baseline that ignores the inputs; McNemar's test of the best model against each other model; learning curves; a cut-off chosen on cross-validated training predictions for the lowest cost (a missed patient costs 4, a false alarm costs 1, an assumption stated in the SPEC) and then checked on the test set; a reliability diagram, Brier score and a recalibrated copy of the best model; and an error analysis that compares the inputs of caught, missed and falsely flagged cases and shows how accuracy depends on the model's confidence. Each finding is one sentence in `outputs/heart/key_findings.csv`.

## Limits

- **Small and old.** 303 patients from one hospital in the 1980s. With 76 test patients, one patient moves accuracy by 1.3 points.
- **A referred population.** Everyone was already sent for angiography because a doctor suspected heart disease. That is why "no chest pain" is the strongest sign of disease here: those patients were referred for some other serious reason. The model would mislead on the general public.
- **Specialist inputs.** The thallium scan and fluoroscopy are among the strongest inputs, and they are only done once disease is suspected. A tool that needs them can't screen anyone early.
- **Mostly men.** 68% of the Cleveland patients are men, so the models know less about women.
- **One label.** Artery narrowing over 50% is a single measurement, not a diagnosis of the whole patient.
- **It doesn't transfer.** At the other hospitals the share of sick patients and the recorded tests differ, and accuracy drops from 80% to between 46% and 85%. A model has to be checked on the population it will be used on.
- **Missing a sick patient costs more than a false alarm.** The 50% cut-off treats them as equal; a screening tool would lower it and accept more false alarms.
