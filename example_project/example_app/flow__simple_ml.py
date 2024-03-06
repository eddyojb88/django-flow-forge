from django_flow_forge.flow_engine import register_task_flow
from django_flow_forge.models import ExecutedFlow, MLResult

from datetime import datetime
from sklearn.datasets import make_classification
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

from sklearn.model_selection import train_test_split
import xgboost as xgb

def fetch_data1():
    return

def clean_data():
    # Load some data, clean it then store it
    return True

def analyze_data():
    # Simple analysis - just summarizing the data
    analysis = 'Some Summary Analysis'
    return {'forecast_date': str(datetime.now()), 'analysis': analysis}

def train_model(**kwargs):
    # Generating synthetic data for demonstration
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
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
    
    # Predictions
    y_pred = model.predict(dtest)
    y_pred_binary = (y_pred > 0.5).astype(int)  # Converting probabilities to binary output

    # Metrics
    conf_matrix = confusion_matrix(y_test, y_pred_binary)
    accuracy = accuracy_score(y_test, y_pred_binary)
    precision = precision_score(y_test, y_pred_binary)
    recall = recall_score(y_test, y_pred_binary)
    f1 = f1_score(y_test, y_pred_binary)

    # Storing metrics in a dictionary
    metrics = {
        'confusion_matrix': conf_matrix.tolist(),  # Converting numpy array to list for JSON serialization
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

    executed_flow = ExecutedFlow.objects.get(pk=kwargs['executed_flow_id'])
    ml_result = MLResult.objects.create()
    ml_result.executed_flow = executed_flow
    ml_result.experiment = 'Experiment with synthetic data.'
    ml_result.algorithm = 'xgboost'
    ml_result.parameters = params
    ml_result.metrics = metrics
    ml_result.save()

    return

def register_pipelines():

    register_task_flow(
        flow_name='pipeline_simple_ml', 
        clear_existing_flow_in_db=True,
        pipeline = {
                    'fetch_data1': {'function': fetch_data1, 'depends_on': []},
                    'clean_data': {'function': clean_data, 'depends_on': ['fetch_data1']},
                    'analyze_data': {'function': analyze_data, 'depends_on': ['clean_data']},
                    'train_model': {'function': train_model, 'depends_on': ['analyze_data']},
                   }
    )

    return

register_pipelines()