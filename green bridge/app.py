import os
import json
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# App Configuration
st.set_page_config(
    page_title="Green Job Bridge - AI Career Translator",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Database Path
DB_PATH = os.getenv("DATABASE_PATH", "green_jobs.db")

# Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Green-Teal Gradient Hero */
    .hero-container {
        background: linear-gradient(135deg, #0f4c3a 0%, #15803d 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(15, 76, 58, 0.15);
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Card design */
    .job-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #16a34a;
        transition: transform 0.2s ease;
    }
    
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    
    .job-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    
    .job-meta {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 0.75rem;
    }
    
    .job-badge {
        background-color: #f0fdf4;
        color: #166534;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        border: 1px solid #bbf7d0;
    }
    
    /* Progress bar */
    .match-container {
        display: flex;
        align-items: center;
        margin-top: 0.5rem;
    }
    
    .match-label {
        font-weight: 600;
        font-size: 0.9rem;
        color: #16a34a;
        margin-right: 1rem;
        min-width: 90px;
    }
    
    .progress-bg {
        background-color: #e2e8f0;
        border-radius: 9999px;
        height: 8px;
        width: 100%;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #16a34a 0%, #059669 100%);
        border-radius: 9999px;
        height: 8px;
    }
    
    /* Sidebar adjustments */
    .css-1d391tw {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get database connection
def get_db_connection():
    return sqlite3.connect(DB_PATH)

# Helper function to compute cosine similarity
def cosine_similarity_calc(a, b):
    a = np.array(a)
    b = np.array(b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

# Retrieve API Key from Environment or Streamlit Secrets
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

# Navigation
with st.sidebar:
    st.markdown("## 🌿 Green Job Bridge")
    st.markdown("AI-Powered Career Transition Tool")
    
    page = st.radio(
        "Navigate",
        ["🗺️ Career Translator", "📊 Match Insights", "🌱 About the Mission"]
    )
    
    st.markdown("---")
    if api_key:
        st.success("Gemini API Connection: Live")
    else:
        st.warning("Running in Demo Mode (Local Mock Embeddings)")
        st.info("To enable AI-powered matching, set the GEMINI_API_KEY environment variable.")

# 🗺️ Career Translator Page
if page == "🗺️ Career Translator":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Discover Your Green Career Path</div>
        <div class="hero-subtitle">Find out how your traditional skills translate to the sustainable economy of tomorrow.</div>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area(
        "Tell us about your work experience (e.g., job title, daily tasks, key skills, industry):",
        height=150,
        placeholder="Example: I am a retail store manager with 8 years of experience. I handle inventory, lead a team of 15 people, manage budgets, ensure customer satisfaction, and coordinate with vendors."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_btn = st.button("Translate My Skills", type="primary", use_container_width=True)
        
    if submit_btn:
        # Validate Input
        words = user_input.strip().split()
        if len(user_input.strip()) == 0:
            st.error("Please tell us about your current role or experience.")
        elif len(words) < 10:
            st.error("Please add more details about your responsibilities (at least 2-3 sentences) so the AI can build an accurate semantic profile.")
        elif len(words) > 500:
            st.warning("Your input is a bit long! Trimming it to the first 500 words to respect API token boundaries.")
            user_input = " ".join(words[:500])
            
        else:
            with st.spinner("Analyzing skills and matching with green roles..."):
                try:
                    # Step 1: Check database initialized
                    if not os.path.exists(DB_PATH):
                        st.error("Database not initialized. Please run 'python init_db.py' first.")
                        st.stop()
                        
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM green_jobs")
                    count = cursor.fetchone()[0]
                    if count == 0:
                        st.error("Database is empty. Please run 'python init_db.py' to seed jobs.")
                        conn.close()
                        st.stop()
                    
                    # Step 2: Get user input embedding
                    # Compute stable mock vector or call Gemini API
                    user_vec = None
                    if not api_key:
                        # Fallback mock embedding
                        np.random.seed(abs(hash(user_input)) % (2**32))
                        user_vec = np.random.randn(768)
                        user_vec /= np.linalg.norm(user_vec)
                        user_vec = user_vec.tolist()
                    else:
                        try:
                            genai.configure(api_key=api_key)
                            embed_res = genai.embed_content(
                                model="models/gemini-embedding-2",
                                content=user_input,
                                task_type="retrieval_query"
                            )
                            user_vec = embed_res['embedding']
                        except Exception as e:
                            st.error(f"Error calling Gemini Embedding API: {e}")
                            st.info("Falling back to local demo matching...")
                            np.random.seed(abs(hash(user_input)) % (2**32))
                            user_vec = np.random.randn(768)
                            user_vec /= np.linalg.norm(user_vec)
                            user_vec = user_vec.tolist()
                    
                    # Step 3: Fetch all job embeddings and compute cosine similarity
                    cursor.execute("SELECT id, title, description, category, required_skills, salary_range, growth_outlook, embedding FROM green_jobs")
                    rows = cursor.fetchall()
                    
                    matches = []
                    for row in rows:
                        job_id, title, desc, cat, skills, salary, outlook, emb_json = row
                        emb = json.loads(emb_json)
                        score = cosine_similarity_calc(user_vec, emb)
                        matches.append({
                            "id": job_id,
                            "title": title,
                            "description": desc,
                            "category": cat,
                            "skills": skills,
                            "salary": salary,
                            "outlook": outlook,
                            "score": score
                        })
                    
                    # Sort matches by score descending
                    matches = sorted(matches, key=lambda x: x["score"], reverse=True)
                    top_matches = matches[:5]
                    
                    # Step 4: Check if any matches are reasonable
                    if top_matches[0]["score"] < 0.25 and not api_key:
                        st.warning("We couldn't find a strong match. Try adding more details about your skills and responsibilities.")
                    
                    # Step 5: Save analytics to match_history
                    # Anonymize user input if desired, but here we store as logged
                    for tm in top_matches[:1]: # Log the top match
                        cursor.execute("""
                        INSERT INTO match_history (user_input, matched_job_id, similarity_score)
                        VALUES (?, ?, ?)
                        """, (user_input[:200] + "...", tm["id"], tm["score"]))
                    conn.commit()
                    conn.close()
                    
                    # Display Results
                    st.success("Successfully translated skills! Here are your top matches:")
                    
                    col_results, col_report = st.columns([2, 3])
                    
                    with col_results:
                        st.markdown("### 🎯 Top 5 Green Economy Matches")
                        for idx, match in enumerate(top_matches):
                            score_pct = int(match["score"] * 100) if api_key else int((match["score"] + 1) / 2 * 100) # Norm for mock
                            if score_pct > 100: score_pct = 100
                            if score_pct < 0: score_pct = 0
                            
                            st.markdown(f"""
                            <div class="job-card">
                                <div class="job-title">{idx+1}. {match['title']}</div>
                                <div class="job-meta">
                                    <span class="job-badge">{match['category']}</span>
                                    <span class="job-badge">{match['outlook']}</span>
                                    <span class="job-badge">{match['salary']}</span>
                                </div>
                                <div style="font-size:0.9rem; color:#475569; margin-bottom:0.75rem;">
                                    {match['description']}
                                </div>
                                <div class="match-container">
                                    <div class="match-label">Match Score: {score_pct}%</div>
                                    <div class="progress-bg">
                                        <div class="progress-fill" style="width: {score_pct}%;"></div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    with col_report:
                        st.markdown("### 📝 Personalized Skill Translation Report")
                        
                        report_placeholder = st.empty()
                        report_placeholder.info("Generating your personalized transition pathway...")
                        
                        # Generate Prompt
                        prompt = f"""
                        You are a career transition expert. A user with the following background:
                        "{user_input}"

                        has been matched to these 5 green/digital jobs:
                        1. {top_matches[0]['title']} (Similarity Match: {int(top_matches[0]['score']*100)}%)
                        2. {top_matches[1]['title']} (Similarity Match: {int(top_matches[1]['score']*100)}%)
                        3. {top_matches[2]['title']} (Similarity Match: {int(top_matches[2]['score']*100)}%)
                        4. {top_matches[3]['title']} (Similarity Match: {int(top_matches[3]['score']*100)}%)
                        5. {top_matches[4]['title']} (Similarity Match: {int(top_matches[4]['score']*100)}%)

                        Generate a personalized, encouraging, and actionable "Skill Translation Report" with:
                        1. A warm, empathetic introduction acknowledging their current experience
                        2. For each of the top 3 jobs: explain WHY their skills transfer (be specific — connect their actual experience to the job requirements)
                        3. Identify 1-2 specific skill gaps for each job (e.g., "You need to learn basic Excel pivot tables" or "You should understand basic solar PV terminology")
                        4. Recommend 1-2 FREE or low-cost resources (YouTube playlists, Coursera, Google Certificates, LinkedIn Learning) for each gap
                        5. A closing section with 3 concrete next steps they can take TODAY
                        6. Keep the tone hopeful, practical, and empowering — this is a life-changing moment for them.
                        """
                        
                        report_text = ""
                        if not api_key:
                            # Demo fallback report
                            report_text = f"""
### 🌿 Demo Career Transition Pathway

Hello! Thank you for sharing your experience. Even in this offline Demo Mode, we can see how your background is highly valuable.

#### 1. {top_matches[0]['title']}
* **Why your skills transfer**: Your experience with coordination, team safety, and workflow management maps perfectly to the operational oversight required for this role.
* **Skill Gap**: Basic certification or foundational vocabulary in this green sector.
* **Free Resource**: YouTube - foundational playlists on environmental processes.

#### 2. {top_matches[1]['title']}
* **Why your skills transfer**: Technical troubleshooting and logistical coordination overlap with planning layouts and equipment logistics.
* **Skill Gap**: Familiarity with specialized software tools or safety certifications.
* **Free Resource**: Coursera - introductory courses (audit for free).

#### 3. {top_matches[2]['title']}
* **Why your skills transfer**: Attention to detail and quality compliance align directly with inspections and compliance guidelines.
* **Skill Gap**: Understanding of specific high-voltage safety standards.
* **Free Resource**: Google Career Certificates.

#### 🏁 3 Concrete Steps for Today:
1. **Research**: Read more about the day-to-day work of a **{top_matches[0]['title']}**.
2. **Skill-up**: Bookmark a free introductory course online.
3. **Network**: Find 2-3 professionals on LinkedIn with this job title and review their career paths.

*Note: For a fully personalized AI report, please set up the Google Gemini API key.*
"""
                            report_placeholder.markdown(report_text)
                        else:
                            try:
                                # Use gemini-1.5-flash
                                model = genai.GenerativeModel("gemini-1.5-flash")
                                response = model.generate_content(prompt)
                                report_text = response.text
                                report_placeholder.markdown(report_text)
                            except Exception as e:
                                st.error(f"Error calling Gemini Text Generation API: {e}")
                                report_text = "Failed to generate report. Please verify your API limits or key."
                                report_placeholder.error(report_text)
                        
                        # Copy/Download Section
                        if report_text:
                            st.download_button(
                                label="📥 Download Translation Report (.md)",
                                data=report_text,
                                file_name="green_job_translation_report.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                            
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

# 📊 Match Insights (Analytics) Page
elif page == "📊 Match Insights":
    st.title("📊 Translation Analytics & Insights")
    st.markdown("Discover the most popular green transition pathways and demand trends.")
    
    if not os.path.exists(DB_PATH):
        st.warning("Database not initialized yet. Please run translations to populate analytics.")
    else:
        conn = get_db_connection()
        # Query total matches count
        df_history = pd.read_sql_query("""
            SELECT h.user_input, h.similarity_score, h.created_at, j.title, j.category 
            FROM match_history h 
            JOIN green_jobs j ON h.matched_job_id = j.id
        """, conn)
        
        conn.close()
        
        if df_history.empty:
            st.info("No matching history recorded yet. Perform some skill translations first!")
        else:
            # Stats row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Skill Translations", len(df_history))
            with col2:
                st.metric("Avg. Match Confidence", f"{int(df_history['similarity_score'].mean() * 100)}%")
            with col3:
                st.metric("Top Transition Sector", df_history['category'].mode()[0] if not df_history.empty else "N/A")
            
            # Layout Charts
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Top Matched Green Sectors")
                sector_counts = df_history['category'].value_counts().reset_index()
                sector_counts.columns = ['Sector', 'Count']
                fig_sector = px.bar(
                    sector_counts, 
                    x='Count', 
                    y='Sector', 
                    orientation='h',
                    color='Count',
                    color_continuous_scale='Greens',
                    labels={'Count': 'Translations'}
                )
                fig_sector.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig_sector, use_container_width=True)
                
            with c2:
                st.markdown("### Top Matched Job Roles")
                job_counts = df_history['title'].value_counts().head(5).reset_index()
                job_counts.columns = ['Job Title', 'Count']
                fig_jobs = px.pie(
                    job_counts,
                    values='Count',
                    names='Job Title',
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                fig_jobs.update_layout(height=350)
                st.plotly_chart(fig_jobs, use_container_width=True)

            # Raw list
            st.markdown("### Recent Transitions Log")
            st.dataframe(
                df_history[['created_at', 'title', 'category', 'similarity_score']].rename(
                    columns={
                        'created_at': 'Timestamp',
                        'title': 'Matched Job Title',
                        'category': 'Sector',
                        'similarity_score': 'Score'
                    }
                ).sort_values(by='Timestamp', ascending=False).head(10),
                use_container_width=True
            )

# 🌱 About the Mission Page
elif page == "🌱 About the Mission":
    st.title("🌱 Connecting People to the Green Future")
    
    st.markdown("""
    ### The Problem
    Traditional career portals rely heavily on exact keyword matching. If a logistics planner with 10 years of experience 
    searches for a job, they are matched with warehouse roles. The algorithms fail to recognize that the planner's underlying skills 
    — capacity routing, safety compliance, vendor coordination, and team management — are highly transferable to emerging roles like 
    **EV Fleet Manager** or **Solar Site Supervisor**.
    
    ### The Solution: Green Job Bridge
    Green Job Bridge uses **semantic AI embeddings** to extract structural competencies from work experience and map them to 
    green and digital career tracks.
    
    - **No Keyword Dependence**: By comparing dense mathematical vectors, the engine finds roles with similar functional responsibilities, even if they share zero keywords.
    - **Closing the Skill Gap**: Instead of just matching, the app details the path forward by identifying exactly what needs to be learned and directing the user to free resources.
    
    ### Supported Sectors
    Our database contains over 500 hand-curated green economy jobs spanning:
    - ☀️ **Solar Energy** (PV design, site operations, integration engineering)
    - 💨 **Wind Energy** (Turbine logistics, resource analysis, turbine maintenance)
    - ⚡ **EV & Battery Systems** (BMS development, charger station installation, fleet transformation)
    - 📊 **Data & Digital** (AI annotation, automation systems, IoT modeling)
    - 🌿 **Sustainability & Operations** (ESG compliance, LCA analysis, circular design)
    """)
    
    st.info("Built with Streamlit, SQLite, Google Gemini, and Numpy. Dedicated to helping workers navigate the climate transition.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>"
    "Green Job Bridge © 2026. Empowering career transitions to a sustainable future."
    "</div>",
    unsafe_allow_html=True
)
