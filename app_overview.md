### What this is

Estimates whether a patient has heart disease from 13 routine measurements, with a **Decision Tree** and **Naive Bayes**. It learns from 303 patients referred to the Cleveland Clinic for a heart X-ray in the 1980s; 46% of them had at least one main artery more than half blocked.

**Educational only.** It can't diagnose anyone, and the limits below are the main lesson.

### How the two models decide

- **Decision Tree**: a flowchart of yes/no questions learned from the data, such as "is the thallium scan normal?" or "is the highest heart rate above 143?". You can follow every step.
- **Naive Bayes**: for each measurement it learns how common the value is among patients with and without heart disease, multiplies those chances and picks the likelier diagnosis. "Naive" because it treats the measurements as unrelated to each other.

A **Random Forest** is a benchmark beyond the course, and **Always healthy** is the floor.

### What to try

- **Assess**: start from a typical or a real test patient, change the values and see each model's verdict with its reasons.
- **Rules**: every rule the tree learned.
- **Results**: test scores, the cut-off trade-off, other hospitals, mistakes and which inputs matter.

### What was found

- **Naive Bayes does best** on the 76 test patients: 80% correct, ROC-AUC 0.86, as good as the Random Forest. The tree is easier to follow but weaker (75%, 0.78).
- **Both miss sick patients.** At the usual 50% cut-off Naive Bayes misses 10 of 35 patients with heart disease. Lowering the cut-off to 20% misses 6 but raises false alarms from 5 to 12.
- **The scan results matter most**: the thallium scan, the number of arteries seen in fluoroscopy and the ST drop in the exercise test. Patients with **no chest pain** are the most likely to be sick, because they were sent for the X-ray for some other strong reason.
- **It doesn't travel.** In Budapest the models hold up (ROC-AUC 0.91 for Naive Bayes). In Switzerland and Long Beach, where most patients were sick and the scans were mostly not recorded, accuracy falls to between 46% and 70%.

### Limits

- 303 patients from one hospital in the 1980s, 68% of them men, all already referred for a heart X-ray. It says nothing about the general population.
- The diagnosis is one measurement (artery narrowing over 50%), not a full clinical picture.
- Several inputs come from specialist tests (thallium scan, fluoroscopy) that only happen after a doctor suspects heart disease.

Code and every figure: [github.com/pxnz3r/disease-risk](https://github.com/pxnz3r/disease-risk).
