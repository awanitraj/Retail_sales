import pandas as pd
from database import engine

def run_etl():
    df = pd.read_excel('data/online_retail.xlsx')
    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    df['CustomerID'] = df['CustomerID'].astype(int).astype(str)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    customers = df[['CustomerID', 'Country']].drop_duplicates(subset=['CustomerID']).rename(columns={'CustomerID': 'customer_id', 'Country': 'country'})
    customers.to_sql('dim_customer', engine, if_exists='append', index=False)

    products = df[['StockCode', 'Description', 'UnitPrice']].drop_duplicates(subset=['StockCode']).rename(columns={'StockCode': 'product_id', 'Description': 'description', 'UnitPrice': 'current_unit_price'})
    products.to_sql('dim_product', engine, if_exists='append', index=False)

    sales = df[['InvoiceNo', 'CustomerID', 'StockCode', 'InvoiceDate', 'Quantity', 'TotalAmount']].rename(columns={'InvoiceNo': 'invoice_no', 'CustomerID': 'customer_id', 'StockCode': 'product_id', 'InvoiceDate': 'invoice_date', 'Quantity': 'quantity', 'TotalAmount': 'total_amount'})
    sales.to_sql('sales_fact', engine, if_exists='append', index=False)
    print("ETL Completed!")

if __name__ == "__main__":
    run_etl()