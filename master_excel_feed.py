import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from prophet import Prophet

print("🔌 Connecting to Database...")
engine = create_engine('postgresql://awanitraj@localhost:5432/retail_db')

df_raw = pd.read_sql("SELECT customer_id, product_id, DATE(invoice_date) as date, total_amount FROM sales_fact", engine)
df_rev = pd.read_sql("SELECT date, total_revenue FROM mv_daily_revenue", engine)


print("🧠 Calculating RFM & Churn...")
df_rfm = df_raw.groupby('customer_id').agg({
    'date': lambda x: (pd.Timestamp.now() - pd.to_datetime(x).max()).days,
    'customer_id': 'count',
    'total_amount': 'sum'
}).rename(columns={'date': 'recency', 'customer_id': 'frequency', 'total_amount': 'monetary'}).reset_index()

df_rfm['r'] = pd.qcut(df_rfm['recency'].rank(method='first'), 4, labels=[4,3,2,1])
df_rfm['f'] = pd.qcut(df_rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4])

def get_segment(row):
    if row['r'] == 4 and row['f'] == 4: return "VIP"
    elif row['r'] == 1: return "At Risk"
    elif row['f'] == 4: return "Loyal"
    else: return "Regular"
df_rfm['segment'] = df_rfm.apply(get_segment, axis=1)


threshold = df_rfm['recency'].median()
df_rfm['churn_flag'] = (df_rfm['recency'] > threshold).astype(int)
clf = RandomForestClassifier(n_estimators=100)
clf.fit(df_rfm[['recency','frequency','monetary']], df_rfm['churn_flag'])
df_rfm['churn_risk_percent'] = (clf.predict_proba(df_rfm[['recency','frequency','monetary']])[:,1] * 100).round(1)


print("📈 Forecasting Future Demand...")
df_prophet = df_rev.rename(columns={'date': 'ds', 'total_revenue': 'y'})
m = Prophet()
m.fit(df_prophet)
future = m.make_future_dataframe(periods=30)
forecast = m.predict(future)
forecast_export = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'projected_revenue'})

print("💾 Exporting Feeds...")
df_rev.to_csv("feed_revenue.csv", index=False)
df_rfm.to_csv("feed_customers.csv", index=False)
forecast_export.to_csv("feed_forecast.csv", index=False)
print("✅ Feeds ready for Excel!")