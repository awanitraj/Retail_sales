import pandas as pd
from sqlalchemy import create_engine

print("🔌 Connecting to Data Warehouse...")
engine = create_engine('postgresql://awanitraj@localhost:5432/retail_db')


cube_query = """
SELECT 
    TO_CHAR(invoice_date, 'YYYY') AS sales_year,
    'Q' || TO_CHAR(invoice_date, 'Q') AS sales_quarter,
    TO_CHAR(invoice_date, 'Mon') AS sales_month,
    product_id,
    SUM(total_amount) AS revenue
FROM 
    sales_fact
WHERE 
    total_amount IS NOT NULL
GROUP BY 
    TO_CHAR(invoice_date, 'YYYY'),
    'Q' || TO_CHAR(invoice_date, 'Q'),
    TO_CHAR(invoice_date, 'Mon'),
    product_id
"""

print("🧊 Building Multi-Dimensional Sales Cube...")
df_cube = pd.read_sql(cube_query, engine)

print("💾 Exporting Cube Feed...")
df_cube.to_csv("feed_sales_cube.csv", index=False)
print("✅ Success! The Sales Cube feed is ready for Excel.")