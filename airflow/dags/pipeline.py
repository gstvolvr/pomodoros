from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import configparser
import os
import sys

from os.path import dirname, join, abspath
query_path = abspath(join(dirname(__file__), '../../'))
sys.path.insert(0, query_path)

from pomodoros import query

config = configparser.ConfigParser()
config.read('config.ini')

args = {
    "owner": "gstvolvr",
    "email": config["pipeline"]["email"],
    "email_on_failure": False,
    "start_date": datetime(2019, 7, 1),
    "retry_delay": timedelta(minutes=1),
    "concurrency": 1
}

dag = DAG('pomodoros', default_args=args, schedule_interval=timedelta(hours=6), max_active_runs=1)

t1 = PythonOperator(
    task_id="query",
    python_callable=query.query_storage_sync,
    retries=15,
    dag=dag
)

cmd = f"{query_path}/bin/push.sh {config['pipeline']['gist_repo']}"
t2 = BashOperator(
    task_id="push",
    bash_command=cmd,
    dag=dag
)

t1 >> t2
