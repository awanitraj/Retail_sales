import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Retail RFM Insights", layout="wide")


def inject_animations():
    st.markdown("""
    <style>
    /* 1. Smooth Fade-In and Slide-Up for the whole page */
    @keyframes fadeInSlideUp {
        0% {
            opacity: 0;
            transform: translateY(20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Apply the animation to the main container */
    .block-container {
        animation: fadeInSlideUp 0.6s ease-out forwards;
    }
    
    /* 2. Hover effect for Metric Cards (KPIs) */
    div[data-testid="metric-container"] {
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        padding: 10px;
        border-radius: 8px;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        background-color: rgba(255, 255, 255, 0.05); /* Slight highlight on dark/light mode */
    }
    </style>
    """, unsafe_allow_html=True)

inject_animations() 

DATABASE_URL = 'postgresql://awanitraj@localhost:5432/retail_db'
engine = create_engine(DATABASE_URL)

@st.cache_data(ttl=60)
def load_data():
    df_rev = pd.read_sql("SELECT date, total_revenue FROM mv_daily_revenue", engine)

    df_seg = pd.read_sql("""
        SELECT 
            ml_segment AS segment, 
            COUNT(customer_id) as c, 
            SUM(monetary) as total_spent,
            AVG(monetary) as avg_spent,
            MAX(monetary) as max_purchase,
            MIN(monetary) as min_purchase
        FROM ml_customer_segments 
        GROUP BY ml_segment
    """, engine)

    df_customers = pd.read_sql("""
        SELECT customer_id, ml_segment AS segment, monetary 
        FROM ml_customer_segments LIMIT 500
    """, engine)

    df_raw = pd.read_sql("""
        SELECT DATE(invoice_date) as date,
               customer_id,
               product_id,
               quantity,
               total_amount
        FROM sales_fact LIMIT 10000
    """, engine)

    return df_rev, df_seg, df_customers, df_raw

df_rev, df_seg, df_customers, df_raw = load_data()

df_rev['date'] = pd.to_datetime(df_rev['date'])
df_raw['date'] = pd.to_datetime(df_raw['date'])

db_max_date = df_raw['date'].max()

st.sidebar.title("🔍 Filters")

db_months = df_raw['date'].dt.strftime('%B %Y').drop_duplicates().tolist()

time_filter = st.sidebar.selectbox(
    "Time Period",
    ["All Time", "Last 15 Days", "Last Quarter"] + db_months
)

products = st.sidebar.multiselect(
    "Products",
    df_raw['product_id'].unique(),
    default=df_raw['product_id'].unique()
)

if time_filter == "Last 15 Days":
    df_raw = df_raw[df_raw['date'] >= (db_max_date - pd.Timedelta(days=15))]
elif time_filter == "Last Quarter":
    df_raw = df_raw[df_raw['date'] >= (db_max_date - pd.Timedelta(days=90))]
elif time_filter != "All Time":
    selected_month = pd.to_datetime(time_filter, format='%B %Y')
    df_raw = df_raw[
        (df_raw['date'].dt.year == selected_month.year) & 
        (df_raw['date'].dt.month == selected_month.month)
    ]

df_raw = df_raw[df_raw['product_id'].isin(products)]

segment_names = {
    0: "Standard Customer",
    1: "High Value Buyer",
    2: "Occasional Shopper",
    3: "Frequent Buyer"
}

df_seg['segment'] = df_seg['segment'].astype(int).map(segment_names)
df_customers['segment'] = df_customers['segment'].astype(int).map(segment_names)

st.title("Retail RFM Insights")
st.markdown("---")

col1, col2, col3 = st.columns(3)

total_rev = df_raw['total_amount'].sum()
total_cust = df_raw['customer_id'].nunique()
avg_order = total_rev / len(df_raw) if len(df_raw) else 0

col1.metric("TOTAL REVENUE", f"₹{total_rev:,.0f}")
col2.metric("TOTAL CUSTOMERS", total_cust)
col3.metric("AVG ORDER", f"₹{avg_order:,.0f}")

st.subheader("Revenue Trend")

rev_trend = df_raw.groupby('date')['total_amount'].sum().reset_index()
st.plotly_chart(px.line(rev_trend, x='date', y='total_amount'), use_container_width=True)

col_bar, col_donut = st.columns(2)

with col_bar:
    st.subheader("Revenue by Segment")
    st.plotly_chart(px.bar(df_seg, x='segment', y='total_spent', color='segment'), use_container_width=True)

with col_donut:
    st.subheader("Customer Distribution")
    
    chart_type = st.selectbox("Select Visual Type", ["Donut Chart (Default)", "Pie Chart", "Bar Chart (Histogram)"])
    
    if chart_type == "Donut Chart (Default)":
        fig = px.pie(df_seg, values='c', names='segment', hole=0.5)
    elif chart_type == "Pie Chart":
        fig = px.pie(df_seg, values='c', names='segment')
    else:
        fig = px.bar(df_seg, x='segment', y='c', color='segment', labels={'c': 'Customer Count'})
        
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Customer Explorer")

seg_filter = st.selectbox("Filter Segment", ["All"] + df_customers['segment'].unique().tolist())

if seg_filter != "All":
    df_customers = df_customers[df_customers['segment'] == seg_filter]

st.dataframe(df_customers, use_container_width=True)
st.subheader("Customer Data Explorer")

all_segments = ["All"] + df_customers['segment'].unique().tolist()
selected_segment = st.selectbox("Filter Customer Table", all_segments)

if selected_segment == "All":
    filtered_df = df_customers
    cat_sum = df_seg['total_spent'].sum()
    cat_max = df_seg['max_purchase'].max()
    cat_min = df_seg['min_purchase'].min()
else:
    filtered_df = df_customers[df_customers['segment'] == selected_segment]
    segment_data = df_seg[df_seg['segment'] == selected_segment].iloc[0]
    cat_sum = segment_data['total_spent']
    cat_max = segment_data['max_purchase']
    cat_min = segment_data['min_purchase']

scol1, scol2, scol3 = st.columns(3)
scol1.metric(f"Total Spent ({selected_segment})", f"₹{cat_sum:,.0f}")
scol2.metric("Highest Purchase", f"₹{cat_max:,.0f}")
scol3.metric("Lowest Purchase", f"₹{cat_min:,.0f}")

st.markdown("<br>", unsafe_allow_html=True) 
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Customer Intelligence")

df_rfm = df_raw.groupby('customer_id').agg({
    'date': lambda x: (db_max_date - x.max()).days,
    'customer_id': 'count',
    'total_amount': 'sum'
}).rename(columns={
    'date': 'recency',
    'customer_id': 'frequency',
    'total_amount': 'monetary'
}).reset_index()

df_rfm['r'] = pd.qcut(df_rfm['recency'].rank(method='first'), 4, labels=[4,3,2,1])
df_rfm['f'] = pd.qcut(df_rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4])
df_rfm['m'] = pd.qcut(df_rfm['monetary'].rank(method='first'), 4, labels=[1,2,3,4])

df_rfm['segment'] = df_rfm.apply(
    lambda x: "VIP" if x['r']==4 and x['f']==4 else
              "At Risk" if x['r']==1 else
              "Loyal" if x['f']==4 else "Regular",
    axis=1
)

threshold = df_rfm['recency'].median()
df_rfm['churn'] = (df_rfm['recency'] > threshold).astype(int)

if df_rfm['churn'].nunique() >= 2:
    model = RandomForestClassifier()
    X = df_rfm[['recency','frequency','monetary']]
    y = df_rfm['churn']
    model.fit(X,y)
    df_rfm['churn_prob'] = model.predict_proba(X)[:,1]
else:
    df_rfm['churn_prob'] = 0

df_rfm['action'] = df_rfm['segment'].map({
    "VIP": "Reward loyalty",
    "At Risk": "Send discount",
    "Loyal": "Upsell",
    "Regular": "Marketing campaign"
})

st.dataframe(df_rfm[['customer_id','segment','churn_prob','action']].head(20), use_container_width=True)

st.markdown("---")
st.subheader("Drill-down Analysis")

product = st.selectbox("Select Product", df_raw['product_id'].unique())

drill = df_raw[df_raw['product_id']==product]
drill = drill.groupby('date')['total_amount'].sum().reset_index()

st.plotly_chart(px.line(drill, x='date', y='total_amount'), use_container_width=True)

st.markdown("---")
st.subheader("Sales Cube Trend Analysis")

df_raw['year'] = df_raw['date'].dt.year.astype(str)
df_raw['month'] = df_raw['date'].dt.strftime('%b')

cols = df_raw.columns.tolist()

rows = st.multiselect("Rows (Dimensions)", cols, default=["year", "month"])
columns = st.multiselect("Columns (Dimensions)", cols, default=["product_id"])
values = st.selectbox("Values (Metrics)", cols, index=cols.index("total_amount"))

if rows and columns:
    pivot = pd.pivot_table(df_raw, index=rows, columns=columns, values=values, aggfunc="sum")
    st.dataframe(pivot, use_container_width=True)
else:
    st.info("Please select at least one Row and one Column to generate the Cube.")

st.subheader("📊 Smart Comparison Insights")

def get_range(days):
    return df_raw[df_raw['date'] >= db_max_date - pd.Timedelta(days=days)]

ranges = {
    "7 Days": get_range(7),
    "15 Days": get_range(15),
    "1 Month": get_range(30),
    "Quarter": get_range(90),
    "Year": get_range(365)
}

period_revenue = {}
for name, df in ranges.items():
    period_revenue[name] = df['total_amount'].sum()

periods = list(period_revenue.keys())

growth_data = []
for i in range(1, len(periods)):
    prev = period_revenue[periods[i-1]]
    curr = period_revenue[periods[i]]

    growth = ((curr - prev) / prev * 100) if prev > 0 else 0

    growth_data.append({
        "Period": periods[i],
        "Growth %": round(growth, 2)
    })

growth_df = pd.DataFrame(growth_data)

st.dataframe(growth_df, use_container_width=True)

best_period = max(period_revenue, key=period_revenue.get)
worst_period = min(period_revenue, key=period_revenue.get)

col1, col2 = st.columns(2)

col1.metric("🏆 Best Period", best_period, f"₹{period_revenue[best_period]:,.0f}")
col2.metric("⚠️ Weakest Period", worst_period, f"₹{period_revenue[worst_period]:,.0f}")

st.subheader("📉 Normalized Trend (Per Day Avg)")

norm_data = []

for name, df in ranges.items():
    if len(df) > 0:
        avg = df['total_amount'].sum() / df['date'].nunique()
        norm_data.append({"Period": name, "Avg Daily Revenue": avg})

norm_df = pd.DataFrame(norm_data)

st.plotly_chart(
    px.bar(norm_df, x="Period", y="Avg Daily Revenue"),
    use_container_width=True
)

st.subheader("🧠 Key Insight")

if growth_df.empty:
    st.info("Not enough data for insights")
else:
    latest_growth = growth_df.iloc[-1]["Growth %"]

    if latest_growth > 10:
        st.success("Strong growth trend detected 🚀")
    elif latest_growth < -10:
        st.error("Revenue declining significantly ⚠️")
    else:
        st.info("Revenue is relatively stable")