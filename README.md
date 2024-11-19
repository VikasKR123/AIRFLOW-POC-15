# Airflow

Airflow is an open-source platform used to schedule, automate, and monitor workflows (tasks or jobs).
It's like a manager that helps organize and run tasks in a specific order ensuring that each task is done at the right time and in the correct sequence.

## key points
> Automates workflows: Handles tasks without manual intervention.
> Monitors: Tracks the status of tasks to ensure they complete successfully.

# DAG  (Directed Acyclic Graph)
It is a way to represent a sequence of tasks in a specific order.
It is like a roadmap that defines how task is executed and their order in which they should be run. It makes sure tasks are executed in the right sequence and only when necessary.


<pre>
  dag = DAG(
    'toxic_comment_classification',
    default_args=default_args,
    description='Pipeline for toxic comment classification using Ray and MLflow',
    schedule_interval=None,
    start_date=datetime(2024, 10, 10),
    catchup=False,
)
</pre>

A DAG() function is used to initialize task in specific order.


----------------------------------------------------------------------------------------------------------------------------------------------------------
<pre>
  train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)
</pre>

The above code is used to creating task named 'train_task' using the PythonOperator. The PythonOperator is used to execute a Python function as part of the DAG workflow.
and 'python_callable=train_model' is used to call function.


----------------------------------------------------------------------------------------------------------------------------------------------------------------------
<pre>   train_task >> model_saved >> task_complted </pre>

This is used to define task dependencies. It specifies the order in which the tasks should be executed, ensuring that each task runs after the previous one completes successfully.

![Screenshot from 2024-11-19 14-31-02](https://github.com/user-attachments/assets/f936140b-5964-4390-a8e1-172353e5a001)





