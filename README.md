# Green Job Bridge 🌿

Green Job Bridge is an AI-powered career translator that helps workers in traditional industries (like retail, manufacturing, and logistics) discover transition pathways into green and digital economy jobs. 

Instead of traditional keyword matching, this tool utilizes **semantic embeddings** to identify transferable skill sets and matches candidates to high-growth sustainability roles. It then generates a personalized, encouraging **Skill Translation Report** mapping their path forward.

---

## Key Features

1. **Semantic Matching Engine**: Uses vector similarity (via Gemini Embeddings or local math fallbacks) to find matches across 500+ pre-seeded green jobs.
2. **Interactive UI**: Clean, responsive Streamlit dashboard with a green/teal palette representing sustainable growth.
3. **Transition Playbooks**: Personalized reports generated on-the-fly detailing why skills transfer, identifying gaps, and recommending free education resources.
4. **Transition Analytics**: A live dashboard visualization of top matched sectors and overall search counts.

---

## Project Structure

```
├── app.py                  # Streamlit Web Application (Frontend + Core ML)
├── init_db.py              # Database Initialization & Job Seeding Script
├── test_matching.py        # Unit Tests for Matching Logic
├── GEMINI.md               # Coding standards and design instructions
├── requirements.txt        # Python dependency configuration
├── .gitignore              # Git patterns to ignore
└── .env.example            # Environment configuration template
```

---

## Getting Started

### 1. Prerequisites
- Python 3.9+
- An internet connection (for downloading dependencies and connecting to the Google Gemini API)

### 2. Setup environment
Clone the repository, navigate to the directory, and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your Gemini API key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY=AIzaSy... (Your Google AI Studio API Key)
DATABASE_PATH=green_jobs.db
DEBUG=false
```

### 4. Initialize the Database
Run the pre-population script to create the SQLite tables and seed **510 green job descriptions** with pre-vectorized embeddings:
```bash
python init_db.py
```
> [!NOTE]
> If `GEMINI_API_KEY` is not present in the environment when running `init_db.py`, the database will automatically generate stable mock embeddings. This allows you to test the entire application workflow offline without an API key!

### 5. Run the Web App
Launch the Streamlit server locally:
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## Testing & Verification

Run the unit tests to verify mathematical correctness:
```bash
python -m unittest test_matching.py
```

---

## Deployment

### Streamlit Community Cloud (Recommended)
1. Push the code repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3. Select this repository, the main branch, and specify `app.py` as the entrypoint.
4. Under **Settings -> Secrets**, paste your API key:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key"
   ```
5. Click **Deploy**. Streamlit Cloud will run `init_db.py` automatically or detect the pre-populated SQLite DB if checked in, or you can run database creation tasks on setup.

### Render / Netlify / VPS
Ensure that the environment variable `GEMINI_API_KEY` is populated on the platform hosting provider. The SQLite database will be initialized upon deployment.
