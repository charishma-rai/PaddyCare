# PaddyCare - paddy disease prediction system

A mobile-first web app: check paddy leaves for disease, keep a history, connect with farmers/experts/buyers,
and see government prices and schemes.

## Run it
```
python -m venv .venv
.venv\Scripts\activate          (Windows cmd)   |   source .venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
streamlit run webapp/app.py
```
Open http://localhost:8501. Create an account on the first screen.

## Live market prices (optional)
1. Register for a free account at data.gov.in and create an API key.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste the key.
3. Check it works: `python scripts/test_mandi_api.py` (set DATA_GOV_API_KEY first, see the file).
Without a key the rest of the Info page still works.

## Tests
```
python tests/test_db.py
python tests/test_mandi.py
```

## Folders
- `webapp/` front end: `app.py` (entry + navigation), `views/` (login, home, predict, history, community, info, account),
  `db.py` (accounts, history, posts), `theme.py` (colours, fonts, animated paddy), `services/mandi.py`, `data/gov_info.json`
- `src/inference/` the real MobileNetV2 `predict()` function and photo-quality checks
- `src/knowledge/disease_info.py` advice shown after a prediction (have an agriculture expert review it)
- Empty, for you to fill: `data/`, `notebooks/`, `models/`, `results/`, `src/data`, `src/training`, `src/evaluation`, `src/explain`
- `scripts/` helper scripts, `tests/`, `docs/`

## Trained model setup

PaddyCare uses the trained MobileNetV2 model for live predictions. Copy the
`mobilenetv2_final.keras` file produced by the training notebook into this
project's `models/` folder:

```text
paddy-disease-prediction/
└── models/
    └── mobilenetv2_final.keras
```

The inference code expects the four output classes in this exact order:

1. `bacterial_leaf_blight`
2. `blast`
3. `brown_spot`
4. `normal`

The saved model includes MobileNetV2 preprocessing, so the app resizes uploaded
RGB images to 224 x 224 and passes pixel values in the 0-255 range. TensorFlow
is installed through `requirements.txt`. If the model is stored elsewhere, set
`PADDYCARE_MODEL_PATH` to its full path before starting Streamlit.

The old fabricated demo predictions and fabricated heatmap have been removed.
Grad-CAM visual explanations are not yet implemented; the UI says so rather
than presenting a simulated explanation.

## Things to fill in or check before real users
- `webapp/data/gov_info.json`: confirm every MSP/scheme/help entry on its official site, then set `verified_on`; add KVK phone numbers.
- `src/knowledge/disease_info.py`: expert review of the advice text.
- Live prices were written against the data.gov.in API but could not be tested without a key: run the test script.

## Known limits
- Refreshing the browser signs you out.
- Accounts, history and posts are stored in a local SQLite file (`data/app/`); free hosts can wipe it. Use Supabase/Firebase for real use.
- Phone camera needs HTTPS: deploy (e.g. Streamlit Community Cloud) and open the https link. Put the API key in the host's Secrets settings.
- Posts have no moderation yet.
