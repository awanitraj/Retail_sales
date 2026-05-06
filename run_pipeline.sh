

echo "🚀 Starting Manual Data Pipeline..."

echo "➡️ Step 1: Running ETL..."
python etl_pipeline.py


if [ $? -eq 0 ]; then
    echo "✅ ETL Succeeded!"
else
    echo "❌ ETL Failed! Stopping pipeline."
    exit 1
fi

echo "➡️ Step 2: Running ML Clustering..."
python ml_segmentation.py

if [ $? -eq 0 ]; then
    echo "✅ ML Clustering Succeeded!"
    echo "🎉 Pipeline complete. Data Warehouse is updated."
else
    echo "❌ ML Clustering Failed!"
    exit 1
fi