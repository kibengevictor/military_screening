# Deploying the Military AI Screening app to Render

This document explains recommended steps to deploy the `ai/` service on Render and how to troubleshoot the common issues (TensorFlow memory, sklearn pickles, knowledge graph unpickle errors).

Prerequisites
- A Render account
- Repository with the `ai/` folder committed (contains `app.py`, `scaler.pkl`, `label_encoder.pkl`, `military_screening_cnn.7z` or the extracted model)

Quick deploy steps
1. In the Render dashboard, create a new Web Service.
   - Environment: Python
   - Build command: `pip install -r ai/requirements.txt`
   - Start command: `gunicorn --config ai/gunicorn_conf.py ai.app:app` (or use the `Procfile` included)
   - Root directory: set to the repository root (Render will detect `ai/Procfile`) or set service to point at `/ai` if using monorepo settings.

2. Ensure runtime & build settings
   - Use the `ai/requirements.txt` created in the repo.
   - If you need a specific Python version, set `runtime.txt` or pick it in the Render UI.

3. Required files in repo (or uploaded during deploy)
   - `military_screening_cnn.7z` OR `military_screening_cnn.h5` extracted model file
   - `scaler.pkl` (joblib dump)
   - `label_encoder.pkl` (joblib dump)
   - `military_knowledge_graph.pkl` (optional; if missing, the app will create a default KG or use `ai/kg.py` unpickler mapping)

4. Recommended instance size
   - TensorFlow CPU models are memory-heavy. Choose a service with at least 2-4 GB RAM for small models. If your model is large, select a larger instance.

Post-deploy checks
- Check the service logs for successful component loading:
  - "✅ TensorFlow model loaded"
  - "✅ Scaler loaded"
  - "✅ Label encoder loaded"
  - "✅ Knowledge graph loaded" OR "✅ Default knowledge graph created"
- If you see "InconsistentVersionWarning" or sklearn warnings, re-generate pickles with matching scikit-learn version (see below).

Troubleshooting common errors
- Worker OOM / SIGKILL
  - Symptoms: Gunicorn worker times out or is killed shortly after boot while loading the model.
  - Fixes: Use the `ai/gunicorn_conf.py` (1 worker, longer timeout); increase instance memory; use TF-Serving or a separate model-serving service.

- Can't get attribute 'MilitaryScreeningKG' on <module '_main_'>
  - Cause: KG was pickled from a script's `__main__` context and unpickling under gunicorn can't find the class.
  - Fixes: (1) Recreate the KG pickle after moving the class into an importable module (e.g., `ai/kg.py`), then re-pickle. (2) The app includes a FixUnpickler mapping to `ai/kg.MilitaryScreeningKG` as a fallback.

- "X does not have valid feature names" warning at transform
  - Cause: Scaler was fit on a pandas DataFrame (with `feature_names_in_`) and inference inputs are numpy arrays.
  - Fix: Re-save the scaler after fitting on the intended input shape, or use the included `resave_pickles.py` to re-create pickles with your training CSV. The app also converts numpy arrays to DataFrame using `scaler.feature_names_in_` when available.

Recreating pickles (recommended long-term)
1. Add your training CSV to the repo (or run locally):
   - Example CSV format: header row with feature columns and label column.

2. Use the helper script included in `ai/resave_pickles.py`:
   - Example:
     ```powershell
     python ai\resave_pickles.py --csv data\training.csv --features feat1 feat2 feat3 --label target
     ```
   - This writes `scaler.pkl` and `label_encoder.pkl` using the scikit-learn version installed in the environment.

Health check
- The app exposes `/health` which returns the component readiness. Use this to confirm model & pickles are loaded.

Sample request
```powershell
$payload = @{ sensor_data = (1..561 | ForEach-Object { 0.1 }) } | ConvertTo-Json
Invoke-RestMethod -Method POST -ContentType 'application/json' -Body $payload https://<your-service>.onrender.com/predict
```

If you want, I can also:
- Generate a fresh `military_knowledge_graph.pkl` using `ai/kg.py` and save it into the repo for a clean start.
- Create a small GitHub Action or script to build the artifacts and upload them to the repo during CI.
