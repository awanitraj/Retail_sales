# Enterprise Retail BI Engine 🚀

A full-stack Business Intelligence solution for retail analytics. This project features an interactive Streamlit web dashboard, automated RFM (Recency, Frequency, Monetary) customer segmentation, Machine Learning churn prediction, and automated data pipelines for Excel and Power BI integration.

## 🌟 Key Features

*   **Interactive Web Dashboard:** A sleek, animated Streamlit app (`dashboard.py`) featuring dynamic KPI metrics, time-period filtering, and interactive Plotly charts.
*   **Customer Intelligence (RFM):** Automatically categorizes customers into actionable segments (VIP, Frequent Buyer, Occasional Shopper, At Risk) based on their purchasing behavior.
*   **Machine Learning Churn Prediction:** Utilizes a `RandomForestClassifier` to predict the probability of a customer churning based on their specific RFM metrics.
*   **Sales Cube Analysis:** Simulates an OLAP Cube using Python and Pandas to allow multi-dimensional drill-downs into revenue by Year, Month, and Product.
*   **Automated Excel/Power BI Feeds:** Python scripts (`master_excel_feed.py`, `create_cube_feed.py`) that pre-aggregate database queries and export clean CSV feeds for seamless integration into external BI tools.

## 🛠️ Technology Stack

*   **Backend / Database:** PostgreSQL (`retail_db`)
*   **Data Processing Pipeline:** Python, Pandas, SQLAlchemy, psycopg2
*   **Machine Learning:** Scikit-Learn (RandomForest)
*   **Frontend Dashboard:** Streamlit, Plotly Express
*   **External BI Integrations:** Microsoft Excel (Mac/Windows), Power BI

## 📂 Project Structure
```text
enterprise_bi_engine/
│
├── dashboard.py               # The main Streamlit web application
├── master_excel_feed.py       # Generates overall revenue & customer feeds
├── create_cube_feed.py        # Generates multi-dimensional sales cube feed
├── README.md                  # Project documentation
│
└── .venv/                     # Python virtual environment (ignored in git)


> First,create the folder, navigate into it, build a fresh Python virtual environment, and activate it.

# 1. Create the project directory (if you haven't already)
mkdir -p ~/Desktop/enterprise_bi_engine

# 2. Move into that directory
cd ~/Desktop/enterprise_bi_engine

# 3. Create a fresh Python virtual environment named '.venv'
python3 -m venv .venv

# 4. Activate the virtual environment
source .venv/bin/activate

> Install the Required Packages
Now environment is activated, we need to install all the libraries your Python scripts and Streamlit app rely on.

# Upgrade pip to the latest version just to be safe
pip install --upgrade pip

# Install the core data, machine learning, database, and dashboard libraries
pip install pandas streamlit plotly sqlalchemy scikit-learn psycopg2-binary prophet

> Run the Data Engines (The Backend)
Before starting the web dashboard or opening Excel, we should run our Python engine scripts so they can calculate the initial RFM segments, ML predictions, and multi-dimensional cubes.

# Run the Master Engine (Generates Customers, Revenue, and Forecast CSVs)
python master_excel_feed.py

# Run the Sales Cube Engine (Generates the Drill-down CSV)
python create_cube_feed.py

> Launch the Web Dashboard (The Frontend)
Finally, start up the interactive Streamlit application.

# Spin up the local web server and open the dashboard
streamlit run dashboard.py
