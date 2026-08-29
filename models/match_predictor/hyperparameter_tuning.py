import xgboost as xgb
from sklearn.model_selection import GridSearchCV
import logging
from train import build_advanced_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def tune_model():
    logger.info("Initializing Hyperparameter Tuning for XGBoost...")
    df = build_advanced_dataset()
    
    if df is None or len(df) < 50:
        logger.error("Insufficient data for tuning.")
        return
        
    feature_cols = [
        'home_elo_pre', 'away_elo_pre', 'elo_diff',
        'home_rest_days', 'away_rest_days',
        'poisson_prob_home', 'poisson_prob_draw', 'poisson_prob_away'
    ]
    
    X = df[feature_cols]
    y = df['outcome']
    
    # Define the base model
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        seed=42,
        eval_metric='mlogloss'
    )
    
    # Define the grid of hyperparameters to search
    param_grid = {
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [100, 200],
        'subsample': [0.8, 1.0]
    }
    
    # Setup the grid search
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring='neg_log_loss',  # Log loss is best for probabilistic multi-class models
        cv=3,
        verbose=1,
        n_jobs=-1
    )
    
    logger.info("Running GridSearchCV (this may take a few minutes)...")
    grid_search.fit(X, y)
    
    logger.info("--- Tuning Complete ---")
    logger.info(f"Best Parameters: {grid_search.best_params_}")
    logger.info(f"Best Log Loss Score: {-grid_search.best_score_:.4f}")
    
if __name__ == "__main__":
    tune_model()
