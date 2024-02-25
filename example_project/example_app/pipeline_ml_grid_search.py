from django_mlops.tasks_db import register_task_pipeline

from datetime import datetime
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import xgboost as xgb


# Fetch data function
def fetch_data1():
    # Generating synthetic data for classification
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
    return X, y

# Fetch data function
def fetch_data2():
    # Additional data fetching process
    fetch_data_nested_1()
    fetch_data_nested_2()
    # In a real-world scenario, this could be fetching data from another source
    # Here, we'll just generate some dummy data
    return 'additional_data'

def fetch_data_nested_1():
    return 'nested_data1'

def fetch_data_nested_2():
    return 'nested_data2'

# Cleaning data function
def clean_data():
    # No specific cleaning required for this example
    return True

# Analyzing data function
def analyze_data():
    # Simple analysis - just summarizing the data
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

# Training model function
def train_model():
    # Generating synthetic data for demonstration
    X, y = fetch_data1()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Training XGBoost model
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    
    params = {
        'max_depth': 3,
        'eta': 0.1,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'seed': 42
    }
    
    num_rounds = 100
    model = xgb.train(params, dtrain, num_rounds, evals=[(dtest, 'eval')], verbose_eval=False)
    
    return model

def clean_data():
    return True

def analyze_data():
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

def train_model():
    print("Training model")

def register_pipelines():

    register_task_pipeline(
        process_name='pipeline_ml_with_grid_search', 
        clear_existing_process_in_db=True,
        pipeline = {
                    'fetch_data2': {'function': fetch_data2, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1', 'fetch_data2']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data']},
                   }
    )

    return

register_pipelines()