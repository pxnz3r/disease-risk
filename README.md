<div align="center">

<h1>Disease risk</h1>

<p>Estimates whether a patient has heart disease with a Decision Tree and Naive Bayes, and tests how far that holds: at other cut-offs and at other hospitals. Built on the UCI Heart Disease data, with an interactive demo that explains each verdict.

**Educational only. Not a medical tool.**</p>

<p>
<a href="https://github.com/pxnz3r/disease-risk/actions/workflows/ci.yml"><img src="https://github.com/pxnz3r/disease-risk/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
<img src="https://img.shields.io/badge/python-3.14-blue" alt="Python 3.14">
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

<p><a href="docs/results.md">Results</a> · <a href="docs/methodology.md">Methodology</a> · <a href="docs/deploy.md">Deploy the demo</a></p>

<img src="outputs/figures/heart/decision_tree.png" width="720" alt="Top three levels of the Decision Tree">

</div>

## How it works

1. **Load and check** the UCI Heart Disease data from four hospitals.
2. **Tune** a Decision Tree and Naive Bayes with cross-validation on Cleveland Clinic patients, then test again at three other hospitals.
3. **Test how sure the scores are** with bootstrap intervals, a paired test against every rival, learning curves and a baseline that ignores the inputs.
4. **Pick the cut-off** at the lowest cost, assuming a missed patient is four times worse than a false alarm, and check calibration.
5. **Study who gets missed** and **try it** in the Streamlit demo, which uses the tuned cut-off.

## Results

Trained on 227 Cleveland Clinic patients; test set of 76 (stratified), never used for tuning or model choice. 46% of patients have heart disease.

| Model | Accuracy | Balanced accuracy | Recall | Precision | ROC-AUC |
| --- | --- | --- | --- | --- | --- |
| **Naive Bayes** | 0.803 | 0.796 | 0.714 | 0.833 | 0.864 |
| **Decision Tree** (depth 3) | 0.750 | 0.741 | 0.629 | 0.786 | 0.777 |
| Random Forest (benchmark) | 0.789 | 0.780 | 0.657 | 0.852 | 0.865 |
| Always healthy (baseline) | 0.539 | 0.500 | 0 | 0 | 0.500 |

Recall and precision are for heart disease.

- **Naive Bayes matches the forest** on ROC-AUC and beats the tree. The tree's 8 leaves are easy to follow but lose detail.
- **The cut-off decides who is missed.** At 50%, Naive Bayes misses 10 of 35 sick test patients with 5 false alarms; at 20% it misses 6 with 12 false alarms.
- **Scan results matter most**: thallium scan, arteries seen in fluoroscopy, ST drop in the exercise test, and chest pain type. Patients with no chest pain are the most likely to be sick, because something else got them referred.
- **It doesn't travel well.** Scored on three hospitals it never saw:

| Hospital | Patients | With heart disease | Naive Bayes accuracy | Naive Bayes ROC-AUC |
| --- | --- | --- | --- | --- |
| Budapest | 294 | 36% | 0.850 | 0.905 |
| Zurich and Basel | 123 | 94% | 0.699 | 0.768 |
| Long Beach (VA) | 200 | 75% | 0.610 | 0.721 |

At Zurich, Basel and Long Beach most scans weren't recorded and most patients were sick, so the Cleveland rules fit poorly.

Full tables and figures: [docs/results.md](docs/results.md). How it was done and the limits: [docs/methodology.md](docs/methodology.md).

## How sure the results are

**Naive Bayes is good but not clearly best.** Test ROC-AUC 0.864 (95% interval 0.778 to 0.936). Against the tree p = 0.455 and against the forest p = 1.0: with 76 test patients the three cannot be told apart.

**No model overfits.** Training and validation ROC-AUC are within 0.05 for all three.

**The cut-off drops to 0.12.** Assuming a missed patient is 4 times worse than a false alarm, recall rises from 0.71 to 0.83 and the cost per 100 patients falls from 59.2 to 47.4.

**Naive Bayes is overconfident.** Its calibration error is 0.173; the forest gives the most honest chances (Brier 0.153 against 0.179).

**Missed patients look healthy on the treadmill.** ST depression in exercise averages 1.7 for caught patients and 0.23 for missed ones.

Every table and figure behind these is in [docs/results.md](docs/results.md).

## Run it

Needs Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py
uv run streamlit run app.py
```

`main.py` downloads the data once into `data/`, then writes figures, tables and the tree's rules to `outputs/`, models to `models/` and the tables to `docs/results.md`. Outputs and models are committed, so the demo works without running it.

## The demo

- **Overview**: what the project is, how both models decide, what was found and its limits.
- **Assess**: fill in a patient or start from a real test patient, and see each model's verdict: the inputs that pushed Naive Bayes, or the questions the tree asked.
- **Rules**: every rule the tree learned.
- **Results**: model comparison, cut-offs, other hospitals, mistakes, permutation importance and data checks.

## Layout

```
disease_risk/   spec.py (inputs and models), data.py (download, four hospitals),
                explain.py (Naive Bayes evidence, cut-offs, other hospitals), report.py
pxlab/          shared engine (vendored): data checks, pipelines, tuning, evaluation, tree rules, app helpers
main.py         the full study
app.py          the Streamlit demo
docs/           methodology, results, deploy
```

## Data

Janosi, Steinbrunn, Pfisterer and Detrano (1988), [Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease), UCI Machine Learning Repository, CC BY 4.0. Collected at the Cleveland Clinic Foundation, the Hungarian Institute of Cardiology in Budapest, University Hospitals Zurich and Basel, and the VA Medical Center in Long Beach.

## License

MIT
