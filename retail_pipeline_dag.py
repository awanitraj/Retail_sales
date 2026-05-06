from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG('retail_pipeline', start_date=datetime(2023, 1, 1), schedule_interval='@daily', catchup=False) as dag:
    
    task_1 = BashOperator(task_id='etl', bash_command='python /path/to/enterprise_bi_engine/etl_pipeline.py')
    task_2 = BashOperator(task_id='ml', bash_command='python /path/to/enterprise_bi_engine/ml_segmentation.py')
    task_1 >> task_2