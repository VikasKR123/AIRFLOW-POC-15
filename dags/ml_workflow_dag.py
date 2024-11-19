from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import ray
import mlflow
import pandas as pd
import gc
import psutil
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Initialize the DAG
dag = DAG(
    'toxic_comment_classification',
    default_args=default_args,
    description='Pipeline for toxic comment classification using Ray and MLflow',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Functions
def auto_garbage_collect(pct=80.0):
    
    if psutil.virtual_memory().percent >= pct:
        gc.collect()

def data_original():
    
    data = pd.read_csv('/home/sigmoid/Downloads/archive (1) (3)/train.csv')
    X = data['comment_text']
    y = data[['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']]
    return X, y

def vector_process(X_train, X_test, y_train, y_test):
    
    vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    return X_train_tfidf, X_test_tfidf, vectorizer

def log_with_mlflow(model, vectorizer, X_train_tfidf, y_train):
    
    with mlflow.start_run():
        mlflow.log_param("model_type", "LogisticRegression with OneVsRestClassifier")
        mlflow.log_param("max_features", 10000)
        accuracy = accuracy_score(y_train, model.predict(X_train_tfidf))
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "toxic_comment_model_by_vikas")
        joblib.dump(vectorizer, 'vectorizer.pkl')
        mlflow.log_artifact('vectorizer.pkl', artifact_path='vectorizer')
        mlflow.register_model(
            f"runs:/{mlflow.active_run().info.run_id}/toxic_comment_model_by_vikas", 
            "ToxicCommentModel"
        )

def train_model():
    
    auto_garbage_collect()
    X, y = data_original()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_tfidf, X_test_tfidf, vectorizer = vector_process(X_train, X_test, y_train, y_test)
    model = OneVsRestClassifier(LogisticRegression())
    model.fit(X_train_tfidf, y_train)
    log_with_mlflow(model, vectorizer, X_train_tfidf, y_train)
    
    
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")
    joblib.dump(model, 'toxic_comment_model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')

def model_saved():
    print("model is saved...")
def task_complted():
    print("task complted")

# Define tasks
train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

model_saved = PythonOperator(
    task_id='model_saved',
    python_callable=model_saved,
    dag=dag,
)

task_complted = PythonOperator(
    task_id='task_complted',
    python_callable=task_complted,
    dag=dag,
)


train_task >> model_saved >> task_complted
