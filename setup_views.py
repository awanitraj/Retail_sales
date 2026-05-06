from sqlalchemy import create_engine, text


DATABASE_URL 
engine = create_engine(DATABASE_URL)

create_view_sql = """
CREATE MATERIALIZED VIEW mv_daily_revenue AS
SELECT 
    DATE(invoice_date) AS date, 
    SUM(total_amount) AS total_revenue
FROM sales_fact 
GROUP BY DATE(invoice_date)
ORDER BY DATE(invoice_date);
"""

try:
    with engine.connect() as conn:
        conn.execute(text(create_view_sql))
        conn.commit()
    print("✅ Materialized View 'mv_daily_revenue' created successfully!")
except Exception as e:
    print(f"❌ Error creating view: {e}")
