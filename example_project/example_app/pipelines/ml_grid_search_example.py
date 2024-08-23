from django_flow_forge.models import ExecutedPipeline, MLResult

from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.datasets import make_classification
import xgboost as xgb

from django_flow_forge.pipeline_engine import PipelineBase

class MLGridSearchPipeline(PipelineBase):

    def __init__(self):
        # Initialize instance attributes
        self.pipeline_name = 'ML Grid Search Example'
        self.pipeline = {
            self.fetch_data: {},
            self.clean_data: {'depends_on': [self.fetch_data,],},
            self.grid_search_multiple_models: {'depends_on': [self.clean_data,]},
        }
        # Call the base class's __init__ to register the pipeline
        super().__init__()

    # Fetch data function
    def fetch_data(self):
        # Additional data fetching pipeline
        data = 'some data'
        self.data = data
        return

    # Cleaning data function
    def clean_data(self):
        # pretending to get some data and turn it into X
        X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
        self.X, self.y = X, y
        return

    # Training model function
    def grid_search_multiple_models(self, **kwargs):

        X, y = self.X, self.y
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Define base models
        models = {
            'RandomForestClassifier': RandomForestClassifier(random_state=42),
            'XGBClassifier': xgb.XGBClassifier(seed=42, eval_metric='logloss', use_label_encoder=False)
        }

        # Define parameter grid for each model
        param_grid = {
            'RandomForestClassifier': {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None]
            },
            'XGBClassifier': {
                'n_estimators': [100, 200],
                'max_depth': [3, 4, 5],
                'learning_rate': [0.1, 0.01]
            }
        }

        # Store the best model and score for each classifier
        best_models = {}
        best_scores = {}
        model_results = {}

        for model_name in models:
            print(f"Starting grid search for {model_name}...")
            grid_search = GridSearchCV(estimator=models[model_name], param_grid=param_grid[model_name], scoring='accuracy', cv=3, verbose=1)
            grid_search.fit(X_train, y_train)
            
            best_model = grid_search.best_estimator_
            best_score = grid_search.best_score_
            best_params = grid_search.best_params_

            
            # Store the best model and its score
            best_models[model_name] = best_model
            best_scores[model_name] = best_score
            best_cv_score = grid_search.best_score_

            
            # Evaluate on the test set
            y_pred = best_model.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_pred)
            print(f"Test accuracy of the best {model_name}: {test_accuracy:.4f}\n")

            conf_matrix = confusion_matrix(y_test, y_pred)
            conf_matrix_list = conf_matrix.tolist()  # Convert the NumPy array to a list
            
            metrics = {
                'best_cv_score': best_cv_score,
                'test_accuracy': test_accuracy,
                'confusion_matrix': conf_matrix_list
            }

            executed_pipeline = ExecutedPipeline.objects.get(pk=kwargs['executed_pipeline_id'])
            ml_result = MLResult.objects.create()
            ml_result.executed_pipeline = executed_pipeline
            ml_result.experiment = 'Simple grid Search and store best params.'
            ml_result.algorithm = model_name
            ml_result.parameters = best_params
            ml_result.evaluation_metrics = metrics
            ml_result.save()

        # Optionally, print out the best models and their scores
        for model_name in best_models:
            print(f"Best {model_name}: {best_models[model_name]}")
            print(f"Best CV accuracy: {best_scores[model_name]:.4f}")