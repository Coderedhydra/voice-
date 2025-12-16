# Live Interview Assistant

## Frontend
You can deploy the `frontend/` folder on Netlify:

1. Zip the `frontend/` folder.
2. Upload to Netlify via drag & drop or GitHub.
3. Make sure `index.html` is at the root.
4. Update `BACKEND_URL` in `js/main.js` with your backend endpoint.

## Backend
1. Go to `backend/`
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python app.py`
5. Ensure CORS is enabled for cross-domain requests.
