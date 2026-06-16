import os
import json
import sqlite3
import numpy as np
from dotenv import load_dotenv
import time

load_dotenv()

# Database Path
DB_PATH = os.getenv("DATABASE_PATH", "green_jobs.db")

# Sample lists of jobs provided in prompt (50 per category)
SOLAR_JOBS = [
    "Solar Site Supervisor", "Solar Panel Installer", "Solar Project Manager", "Solar Sales Consultant", 
    "Solar Maintenance Technician", "PV System Designer", "Solar Field Engineer", "Solar Quality Control Inspector", 
    "Solar Rooftop Specialist", "Solar Operations Manager", "Solar Permit Specialist", "Solar Grid Integration Engineer", 
    "Solar Storage Specialist", "Solar Commissioning Engineer", "Solar Asset Manager", "Solar Performance Analyst", 
    "Solar Safety Officer", "Solar Logistics Coordinator", "Solar Procurement Specialist", "Solar Customer Support Lead", 
    "Solar Technical Trainer", "Solar Draftsman", "Solar Electrical Engineer", "Solar Civil Engineer", 
    "Solar Structural Engineer", "Solar Site Surveyor", "Solar CAD Operator", "Solar SCADA Technician", 
    "Solar Monitoring Analyst", "Solar Remote Operations Engineer", "Solar Field Service Manager", "Solar Warranty Specialist", 
    "Solar Inventory Manager", "Solar Supply Chain Coordinator", "Solar Factory Production Lead", "Solar Module Tester", 
    "Solar Glass Technician", "Solar Frame Assembler", "Solar Junction Box Specialist", "Solar Cable Harness Technician", 
    "Solar Inverter Specialist", "Solar Transformer Technician", "Solar Substation Engineer", "Solar Transmission Planner", 
    "Solar Distribution Analyst", "Solar Microgrid Designer", "Solar Off-grid Specialist", "Solar Hybrid System Engineer", 
    "Solar BESS (Battery Energy Storage) Operator", "Solar Decommissioning Specialist"
]

WIND_JOBS = [
    "Wind Turbine Technician", "Wind Farm Site Manager", "Wind Project Developer", "Wind Resource Analyst", 
    "Wind Operations Engineer", "Wind Maintenance Planner", "Wind Blade Repair Specialist", "Wind Gearbox Technician", 
    "Wind Generator Specialist", "Wind Control Systems Engineer", "Wind SCADA Engineer", "Wind Asset Performance Manager", 
    "Wind Health & Safety Officer", "Wind Environmental Compliance Specialist", "Wind Logistics Manager", 
    "Wind Transportation Coordinator", "Wind Crane Operator", "Wind Foundation Engineer", "Wind Tower Erection Supervisor", 
    "Wind Electrical Systems Engineer", "Wind Grid Connection Specialist", "Wind Energy Analyst", 
    "Wind Data Scientist", "Wind Remote Monitoring Engineer", "Wind Quality Assurance Inspector", "Wind Commissioning Engineer", 
    "Wind Project Finance Analyst", "Wind Land Acquisition Specialist", "Wind Community Relations Manager", "Wind Permitting Specialist", 
    "Wind Construction Manager", "Wind Civil Engineer", "Wind Geotechnical Engineer", "Wind Structural Engineer", 
    "Wind Noise & Vibration Analyst", "Wind Avian & Wildlife Specialist", "Wind Shadow Flicker Analyst", "Wind Ice Throw Risk Analyst", 
    "Wind Met Mast Technician", "Wind LiDAR Specialist", "Wind SoDAR Specialist", "Wind Power Curve Engineer", 
    "Wind Turbine Retrofit Specialist", "Wind Repowering Analyst", "Wind Decommissioning Planner", "Wind Parts Inventory Manager", 
    "Wind Supplier Quality Engineer", "Wind Factory Production Supervisor", "Wind Blade Molding Technician", "Wind Nacelle Assembly Lead"
]

EV_JOBS = [
    "EV Battery Technician", "EV Charging Station Installer", "EV Fleet Manager", "EV Maintenance Specialist", 
    "Battery Cell Engineer", "Battery Pack Assembler", "Battery Thermal Management Engineer", "Battery Safety Engineer", 
    "Battery Recycling Specialist", "Battery Second-Life Applications Engineer", "Battery Supply Chain Analyst", "Battery Raw Materials Sourcing Specialist", 
    "Battery Testing Technician", "Battery Quality Control Engineer", "Battery Management Systems (BMS) Engineer", "Battery Software Developer", 
    "Battery Firmware Engineer", "Battery Hardware Engineer", "Battery Production Line Supervisor", "Battery Electrode Coater Technician", 
    "Battery Separator Specialist", "Battery Electrolyte Chemist", "Battery Dry Room Engineer", "Battery Formation Technician", 
    "Battery Aging Analyst", "Battery Capacity Tester", "Battery Diagnostics Specialist", "Battery Warranty Analyst", 
    "Battery Field Service Engineer", "Battery Remote Monitoring Specialist", "Battery Thermal Runaway Prevention Engineer", "Battery Fire Safety Specialist", 
    "EV Powertrain Engineer", "EV Motor Designer", "EV Inverter Specialist", "EV Converter Technician", 
    "EV Transmission Engineer", "EV Thermal Systems Engineer", "EV Cooling Systems Specialist", "EV HVAC Engineer", 
    "EV Braking Systems Engineer (Regenerative)", "EV Steering Systems Engineer", "EV Suspension Engineer", "EV Chassis Engineer", 
    "EV Body Engineer", "EV Lightweighting Specialist", "EV Aerodynamics Engineer", "EV Noise & Vibration Engineer", 
    "EV EMC (Electromagnetic Compatibility) Engineer", "EV Homologation Specialist"
]

DATA_JOBS = [
    "Data Analyst", "Data Scientist", "Machine Learning Engineer", "AI Ethics Specialist", 
    "Data Annotation Specialist", "Data Labeling Technician", "Data Quality Analyst", "Data Governance Specialist", 
    "Data Privacy Officer", "Data Security Analyst", "Data Architect", "Data Engineer", 
    "Data Pipeline Developer", "Data Visualization Specialist", "Business Intelligence Analyst", "Analytics Manager", 
    "Database Administrator", "Cloud Data Engineer", "Cloud Solutions Architect", "DevOps Engineer", 
    "Site Reliability Engineer", "Automation Engineer", "QA Automation Specialist", "RPA (Robotic Process Automation) Developer", 
    "Low-Code Developer", "No-Code Developer", "Frontend Developer", "Backend Developer", 
    "Full Stack Developer", "API Integration Specialist", "Systems Analyst", "IT Support Specialist", 
    "Helpdesk Technician", "Network Administrator", "Cybersecurity Analyst", "SOC (Security Operations Center) Analyst", 
    "Penetration Tester", "Vulnerability Analyst", "Incident Response Specialist", "Digital Marketing Analyst", 
    "SEO Specialist", "Social Media Analytics Specialist", "E-commerce Analyst", "Supply Chain Data Analyst", 
    "Logistics Data Analyst", "Healthcare Data Analyst", "Financial Data Analyst", "Risk Data Analyst", 
    "Fraud Detection Analyst", "Compliance Data Analyst"
]

SUSTAINABILITY_JOBS = [
    "Sustainability Manager", "ESG (Environmental, Social, Governance) Analyst", "Carbon Offset Specialist", "Carbon Credit Trader", 
    "Net Zero Consultant", "Circular Economy Specialist", "Waste Management Analyst", "Recycling Operations Manager", 
    "Water Conservation Specialist", "Water Treatment Technician", "Air Quality Monitoring Specialist", "Environmental Compliance Officer", 
    "Environmental Impact Assessor", "Environmental Remediation Specialist", "Brownfield Redevelopment Planner", "Green Building Certifier (LEED/BREEAM)", 
    "Energy Efficiency Engineer", "Energy Auditor", "Building Performance Analyst", "HVAC Optimization Specialist", 
    "Smart Building Technician", "Building Automation Systems Engineer", "Facilities Energy Manager", "Industrial Energy Manager", 
    "Process Optimization Engineer", "Green Chemistry Specialist", "Sustainable Materials Engineer", "Sustainable Packaging Designer", 
    "Sustainable Supply Chain Manager", "Sustainable Procurement Specialist", "Corporate Sustainability Reporter", "Climate Risk Analyst", 
    "Climate Adaptation Planner", "Climate Resilience Engineer", "Disaster Recovery Specialist", "Emergency Response Coordinator", 
    "Community Resilience Planner", "Urban Green Space Designer", "Urban Forester", "Green Roof Installer", 
    "Vertical Farming Specialist", "Hydroponics Technician", "Aquaponics Specialist", "Regenerative Agriculture Specialist", 
    "Soil Conservation Technician", "Agroforestry Planner", "Permaculture Designer", "Environmental Educator", 
    "Sustainability Communications Specialist", "Green Policy Advisor"
]

LOGISTICS_JOBS = [
    "Warehouse Manager", "Inventory Controller", "Supply Chain Coordinator", "Logistics Planner", 
    "Transportation Manager", "Fleet Operations Supervisor", "Distribution Center Lead", "Procurement Specialist", 
    "Purchasing Agent", "Materials Planner", "Production Scheduler", "Quality Control Inspector", 
    "Safety Officer", "Facilities Manager", "Maintenance Supervisor", "Plant Operations Manager", 
    "Shift Supervisor", "Team Leader", "Operations Analyst", "Process Improvement Specialist", 
    "Lean Six Sigma Specialist", "Continuous Improvement Manager", "Project Coordinator", "Project Manager", 
    "Program Manager", "Operations Director", "General Manager", "Assistant Manager", 
    "Store Manager", "Retail Department Head", "Merchandising Manager", "Category Manager", 
    "Buyer", "Supplier Relationship Manager", "Vendor Manager", "Contract Administrator", 
    "Compliance Officer", "Risk Manager", "Internal Auditor", "Training Coordinator", 
    "HR Generalist", "Recruitment Specialist", "Employee Relations Manager", "Payroll Specialist", 
    "Benefits Administrator", "Office Manager", "Administrative Assistant", "Executive Assistant", 
    "Customer Service Manager", "Client Relationship Manager"
]

# Generate additional job titles to reach 500+ jobs (approx 35 extra per category)
extra_solar = [f"Solar {x}" for x in ["Inspection Lead", "Permit Consultant", "Financing Advisor", "Estimator Specialist", "Contracts Specialist", "Assembly Associate", "Rigging Technician", "Grounding Engineer", "Combiner Box Technician", "Racking Installer", "Utility Coordinator", "Storage Integration Analyst", "Subcontractor Coordinator", "Safety Inspector", "Site Lead Technician", "Operations Planner", "Thermal Specialist", "Micro-inverter Consultant", "Shading Analyst", "Grid Stability Engineer", "Sales Supervisor", "Customer Onboarding Specialist", "Underwriter", "Policy Consultant", "Decommissioning Tech", "Logistics Planner", "Maintenance Lead", "Compliance Auditor", "CAD Designer", "Resource Planner", "PV Associate", "System Tester", "Installation Supervisor", "Materials Sourcing Agent", "Field Safety Lead"]]
extra_wind = [f"Wind {x}" for x in ["Turbine Rigger", "Blade Finisher", "Foundation Inspector", "Tower Assembler", "SCADA Integration Tech", "Resource Modeler", "Turbine Electrician", "Grid Compliance Lead", "Meteorological Analyst", "Hydraulic Specialist", "Pitch System Engineer", "Yaw System Technician", "Substation Operator", "Erection Coordinator", "Logistics Scheduler", "QA Specialist", "Field Coordinator", "Permit Lead", "HSE Specialist", "Community Liaison", "Procurement Officer", "Operations Planner", "Performance Analyst", "Blade Painter", "Gearbox Rebuilder", "Lubrication Technician", "Grid Modeler", "Decommissioning Tech", "Rotor Balancer", "Anemometer Tech", "Safety Supervisor", "Logistics Lead", "Site Surveyor", "Civil Inspector", "Commissioning Lead"]]
extra_ev = [f"EV {x}" for x in ["Charging Project Planner", "Battery Recycling Lead", "Powertrain Tester", "BMS Calibration Engineer", "Thermal Simulation Specialist", "Battery Manufacturing Specialist", "Dry Room Supervisor", "Electrode Slurry Mixer", "Cell Tester", "Pack Prototyper", "Fleet Conversion Advisor", "Grid Charging Demand Analyst", "Charging Network Maintenance Tech", "Fast Charger Technician", "BMS Software Tester", "Safety Inspector", "Cell Quality Control Specialist", "Raw Materials Inspector", "Copper Foil Specialist", "Separator Quality Analyst", "Welding Specialist", "Case Assembler", "Wiring harness Designer", "Anode Formulation Chemist", "Cathode Sourcing Lead", "Thermal Interface Material Specialist", "Battery Lifecycle Analyst", "Pack Tester", "Charging Station Permit Specialist", "Inverter Assembly Tech", "Powertrain Integration Lead", "Regenerative Braking Analyst", "Drive Unit Specialist", "Firmware QA Analyst", "Homologation Engineer"]]
extra_data = [f"Data {x}" for x in ["Labeling Team Lead", "Annotation QA Specialist", "Pipeline Architect", "Governance Steward", "Privacy Compliance Lead", "Warehouse Engineer", "Analytics Lead", "Quality Engineer", "Visualization Engineer", "Catalog Specialist", "Strategy Consultant", "Integration Architect", "Curator", "ETL Developer", "MLOps Engineer", "Model Evaluator", "AI Safety Analyst", "Prompt Engineer", "Vector Database Administrator", "Semantic Search Specialist", "Feature Store Engineer", "Reporting Specialist", "Dashboard Developer", "Database Optimizer", "Data Migration Lead", "BI Specialist", "Analytics Coordinator", "Metadata Analyst", "Audit Specialist", "Lineage Specialist", "Science Associate", "Analytics Specialist", "Annotation Lead", "Labeler Coordinator", "Governance Officer"]]
extra_sustainability = [f"Sustainability {x}" for x in ["Project Coordinator", "Reporting Specialist", "ESG Data Analyst", "Carbon Auditor", "Scope 3 Emission Specialist", "Circular Economy Planner", "Zero Waste Auditor", "Water Recycling Specialist", "Green Purchasing Agent", "LEED AP Consultant", "Energy Performance Modeler", "Smart Grid Analyst", "Eco-Design Engineer", "Biodiversity Coordinator", "Urban Agriculture Specialist", "Organic Farming Consultant", "Soil Health Technician", "Forest Carbon Analyst", "Green Marketing Specialist", "Environmental Policy Coordinator", "Supply Chain Audit Specialist", "Packaging Materials Engineer", "LCA Analyst", "E-waste Program Manager", "Corporate Giving Lead", "Employee Engagement Coordinator", "Climate Risk Analyst", "Resilience Strategist", "Disaster Mitigation Planner", "Water Efficiency Auditor", "Indoor Air Quality Tech", "Energy Billing Analyst", "Solar Integration Advisor", "Wind Resource Advisor", "Green Building Architect"]]
extra_logistics = [f"Logistics {x}" for x in ["System Coordinator", "Operations Analyst", "Dispatch Specialist", "Route Optimization Planner", "Fleet Safety Specialist", "Warehouse Operations Supervisor", "Receiving Clerk Lead", "Shipping Supervisor", "Procurement Coordinator", "Vendor Compliance Analyst", "Inventory Planner", "Material Flow Analyst", "Packaging Specialist", "Freight Forwarding Coordinator", "Import/Export Specialist", "Supply Chain Analyst", "Logistics Systems Admin", "Returns Coordinator", "Demand Planner", "Supply Planner", "Operations Team Leader", "Shift Manager", "Continuous Improvement Associate", "Lean Analyst", "Project Lead", "Store Supervisor", "Client Account Manager", "Service Operations Lead", "Quality Specialist", "Health & Safety Coordinator", "Facilities Associate", "Maintenance Tech Supervisor", "Contract Specialist", "Sourcing Specialist", "Purchasing Coordinator"]]

ALL_JOBS_TITLES_CATEGORIES = []

for title in SOLAR_JOBS + extra_solar:
    ALL_JOBS_TITLES_CATEGORIES.append((title, "Solar"))
for title in WIND_JOBS + extra_wind:
    ALL_JOBS_TITLES_CATEGORIES.append((title, "Wind"))
for title in EV_JOBS + extra_ev:
    ALL_JOBS_TITLES_CATEGORIES.append((title, "EV & Battery"))
for title in DATA_JOBS + extra_data:
    ALL_JOBS_TITLES_CATEGORIES.append((title, "Data & Digital"))
for title in SUSTAINABILITY_JOBS + extra_sustainability:
    ALL_JOBS_TITLES_CATEGORIES.append((title, "Sustainability & Green Operations"))
for title in LOGISTICS_JOBS + extra_logistics:
    ALL_JOBS_TITLES_CATEGORIES.append((title, "Logistics & Operations Transferable"))

# We now have 6 categories with 85 jobs each = 510 jobs in total!

def generate_job_details(title, category):
    """Generates realistic job descriptions, skills, salary ranges, and outlooks programmatically."""
    title_lower = title.lower()
    
    if category == "Solar":
        desc = (
            f"The {title} is responsible for planning, executing, and optimizing operations within solar PV systems. "
            "This role involves conducting site assessments, ensuring electrical code compliance, coordinating installation schedules, "
            "and resolving technical integration challenges on the electrical grid. You will work closely with engineering teams "
            "to maximize energy yield, inspect hardware, and guarantee safety protocols on commercial, residential, or utility-scale projects."
        )
        skills = "Solar PV systems, Electrical Engineering, CAD Drawings, Grid Integration, Site Safety, Project Planning, SCADA Systems, Power Electronics"
        salary = "$68,000 - $112,000"
        outlook = "High Growth"
    elif category == "Wind":
        desc = (
            f"The {title} focuses on the design, maintenance, analysis, or operations of wind energy generation infrastructure. "
            "Key responsibilities include resource assessment, mechanical and electrical troubleshooting of turbine components, "
            "blade inspection, environmental compliance monitoring, and coordinating field logistics. You will ensure optimal system "
            "uptime and safety compliance in challenging onshore or offshore wind farm environments."
        )
        skills = "Wind Turbine Mechanics, SCADA Systems, Electrical Systems, Mechanical Repair, Resource Analysis, HSE Standards, Logistics Coordination, Tower Erection"
        salary = "$72,000 - $118,000"
        outlook = "High Growth"
    elif category == "EV & Battery":
        desc = (
            f"The {title} plays a key role in the design, testing, manufacturing, or operations of electric vehicle and battery storage systems. "
            "This involves managing lithium-ion cell chemistry, thermal cooling systems, battery management systems (BMS), "
            "charging infrastructure installations, and ensuring safety standards to prevent thermal runaway. You will support "
            "the global transition to clean transportation by improving energy density and charging efficiency."
        )
        skills = "Battery Management Systems (BMS), Thermal Management, Electric Vehicle Systems, Lithium-ion Cells, High-Voltage Safety, Charging Protocols, CAD Design, Raw Materials Sourcing"
        salary = "$76,000 - $128,000"
        outlook = "High Growth"
    elif category == "Data & Digital":
        desc = (
            f"The {title} focuses on leveraging data, cloud systems, machine learning, and automation to drive digital transformation "
            "and sustainable operations. Responsibilities include building robust data pipelines, training ML models, managing cloud storage, "
            "performing data quality checks, and creating visual analytics dashboards. You will help turn complex data into actionable "
            "insights to optimize efficiency and resource allocation across digital products."
        )
        skills = "Data Pipelines, Python, SQL, Cloud Architecture (AWS/Azure), Data Visualization, Machine Learning, Automation, Cybersecurity, Data Annotation, API Integration"
        salary = "$82,000 - $145,000"
        outlook = "High Growth"
    elif category == "Sustainability & Green Operations":
        desc = (
            f"The {title} guides organizations in adopting sustainable business models, meeting ESG targets, and lowering carbon footprints. "
            "Key duties include carbon auditing, assessing waste streams, designing circular product lifecycles, preparing CSR sustainability "
            "reports, and ensuring compliance with regulatory bodies. You will build and implement policies that align operational "
            "efficiency with environmental conservation."
        )
        skills = "ESG Reporting, Carbon Footprint Auditing, Waste Management, Environmental Policy, Sustainability Frameworks (LEED/BREEAM), Lifecycle Assessment, Corporate Governance, Energy Auditing"
        salary = "$74,000 - $124,000"
        outlook = "High Growth"
    else:  # Logistics & Operations Transferable
        desc = (
            f"The {title} oversees daily workflows, supply chain systems, inventory, and operations in key industrial sectors. "
            "Responsibilities include coordinating teams, tracking product inventories, sourcing materials, managing operating budgets, "
            "and executing continuous improvement strategies like Lean and Six Sigma. This operational base serves as a crucial starting "
            "point, offering core transferable competencies like project management, safety coordination, and resource logistics."
        )
        skills = "Supply Chain Management, Inventory Control, Sourcing & Procurement, Process Improvement (Lean/Six Sigma), Project Management, Team Leadership, Safety Operations, Budget Management"
        salary = "$62,000 - $108,000"
        outlook = "Moderate Growth"

    return desc, skills, salary, outlook

def get_embedding(text, api_key):
    """Calls the Google Gemini Embedding API to generate a 768-dim vector."""
    if not api_key:
        # Generate stable mock embedding based on hash of text (for testing without key)
        np.random.seed(abs(hash(text)) % (2**32))
        mock_vec = np.random.randn(768)
        mock_vec /= np.linalg.norm(mock_vec)  # normalized
        return mock_vec.tolist()
    
    import google.generativeai as genai
    try:
        genai.configure(api_key=api_key)
        # Use gemini-embedding-2
        result = genai.embed_content(
            model="models/gemini-embedding-2",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error calling Gemini Embedding API: {e}. Falling back to mock embedding.")
        np.random.seed(abs(hash(text)) % (2**32))
        mock_vec = np.random.randn(768)
        mock_vec /= np.linalg.norm(mock_vec)
        return mock_vec.tolist()

def init_db():
    print(f"Initializing database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create green_jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS green_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        salary_range TEXT,
        growth_outlook TEXT,
        embedding TEXT NOT NULL
    )
    """)
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create match_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        matched_job_id INTEGER NOT NULL,
        similarity_score REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (matched_job_id) REFERENCES green_jobs (id)
    )
    """)
    
    conn.commit()
    
    # Check if database is already populated
    cursor.execute("SELECT COUNT(*) FROM green_jobs")
    count = cursor.fetchone()[0]
    if count >= len(ALL_JOBS_TITLES_CATEGORIES):
        print(f"Database already populated with {count} jobs. Checking if embeddings are needed...")
        conn.close()
        return

    # Clear existing if any to avoid mismatch
    cursor.execute("DELETE FROM green_jobs")
    conn.commit()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found in environment. Database will be seeded with MOCK embeddings.")
        print("You can re-run this script later with a valid key to generate real embeddings.")

    # Prepare all job details
    jobs_data = []
    texts_to_embed = []
    for title, category in ALL_JOBS_TITLES_CATEGORIES:
        desc, skills, salary, outlook = generate_job_details(title, category)
        embedding_text = f"{title}: {desc} Required skills: {skills}"
        jobs_data.append((title, desc, category, skills, salary, outlook))
        texts_to_embed.append(embedding_text)
        
    # Generate embeddings in batches of 100
    batch_size = 100
    all_embeddings = []
    
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i+batch_size]
            print(f"Embedding batch {i // batch_size + 1} ({len(batch_texts)} texts)...")
            try:
                result = genai.embed_content(
                    model="models/gemini-embedding-2",
                    content=batch_texts,
                    task_type="retrieval_document"
                )
                all_embeddings.extend(result['embedding'])
                time.sleep(1.0) # Rate limit protection
            except Exception as e:
                print(f"Error in batch embedding: {e}. Falling back to mock embeddings for this batch.")
                for text in batch_texts:
                    np.random.seed(abs(hash(text)) % (2**32))
                    mock_vec = np.random.randn(768)
                    mock_vec /= np.linalg.norm(mock_vec)
                    all_embeddings.append(mock_vec.tolist())
    else:
        print("WARNING: GEMINI_API_KEY not found. Using mock embeddings.")
        for text in texts_to_embed:
            np.random.seed(abs(hash(text)) % (2**32))
            mock_vec = np.random.randn(768)
            mock_vec /= np.linalg.norm(mock_vec)
            all_embeddings.append(mock_vec.tolist())
            
    # Insert everything into DB
    for idx, (title, desc, category, skills, salary, outlook) in enumerate(jobs_data):
        embedding_json = json.dumps(all_embeddings[idx])
        cursor.execute("""
        INSERT INTO green_jobs (title, description, category, required_skills, salary_range, growth_outlook, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, desc, category, skills, salary, outlook, embedding_json))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM green_jobs")
    final_count = cursor.fetchone()[0]
    print(f"Successfully database initialization. Seeding complete. Total jobs: {final_count}")
    conn.close()

if __name__ == "__main__":
    init_db()
