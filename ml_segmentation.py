import pandas as pd
from database import engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def run_ml_clustering():
    query = "SELECT customer_id, (SELECT MAX(invoice_date) FROM sales_fact) - MAX(invoice_date) AS recency_days, COUNT(DISTINCT invoice_no) AS frequency, SUM(total_amount) AS monetary FROM sales_fact GROUP BY customer_id"
    df = pd.read_sql(query, engine)
    df['recency'] = df['recency_days'].dt.days
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[['recency', 'frequency', 'monetary']])
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['ml_segment'] = kmeans.fit_predict(scaled_features).astype(str)
    
    df[['customer_id', 'recency', 'frequency', 'monetary', 'ml_segment']].to_sql('ml_customer_segments', engine, if_exists='replace', index=False)
    print("ML Pipeline Completed!")

if __name__ == "__main__":
    run_ml_clustering()