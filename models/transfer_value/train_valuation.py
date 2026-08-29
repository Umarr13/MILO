import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "../../milo.db"

def build_valuation_dataset():
    """
    Builds the dataset by joining player details with their stats.
    Integrates a supplementary market value dataset (Kaggle Transfermarkt) 
    if `transfermarkt.csv` is present in the directory.
    """
    conn = sqlite3.connect(DB_PATH)
    
    # In a real setup, tier and contract are in the DB or joined from external sources.
    query = """
        SELECT 
            p.id, p.name, p.position, p.date_of_birth, p.nationality,
            s.goals, s.assists, s.minutes_played, s.appearances
        FROM players p
        LEFT JOIN player_stats s ON p.id = s.player_id
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        conn.close()
        return None
        
    conn.close()
    
    if df.empty or len(df) < 50:
        logger.warning("Insufficient player data in DB. Generating synthetic dataset for scaffolding.")
        df = generate_synthetic_data()
    else:
        # Calculate approximate age
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
        current_year = pd.Timestamp.now().year
        df['age'] = current_year - df['date_of_birth'].dt.year
        df['age'].fillna(df['age'].median(), inplace=True)
        
        # Clean stats
        for col in ['goals', 'assists', 'minutes_played', 'appearances']:
            df[col] = df[col].fillna(0)
            
        # Try to integrate Kaggle dataset
        kaggle_path = "transfermarkt.csv"
        if os.path.exists(kaggle_path):
            logger.info("Found Kaggle Transfermarkt dataset. Integrating...")
            tm_df = pd.read_csv(kaggle_path)
            # Assuming the CSV has columns: player_name, market_value_m, tier, contract_years_left
            df = df.merge(tm_df, left_on='name', right_on='player_name', how='left')
        else:
            logger.warning("Kaggle Transfermarkt dataset not found. Simulating market value, tier, and contract.")
            df['market_value_m'] = simulate_market_value(df)
            df['tier'] = np.random.choice([1, 2, 3, 4], len(df), p=[0.4, 0.3, 0.2, 0.1])
            df['contract_years_left'] = np.random.uniform(0.5, 5.0, len(df))
    
    # Feature Engineering
    df['goal_contribution'] = df['goals'] + df['assists']
    df['mins_per_appearance'] = np.where(df['appearances'] > 0, df['minutes_played'] / df['appearances'], 0)
    
    df = df.dropna(subset=['position'])
    
    return df

def generate_synthetic_data(n_samples=1000):
    """Generates realistic player data when DB is empty."""
    np.random.seed(42)
    positions = ['Attacker', 'Midfielder', 'Defender', 'Goalkeeper']
    data = {
        'id': range(1, n_samples + 1),
        'position': np.random.choice(positions, n_samples, p=[0.2, 0.4, 0.3, 0.1]),
        'age': np.random.normal(26, 4, n_samples).clip(16, 40),
        'goals': np.random.exponential(3, n_samples).astype(int),
        'assists': np.random.exponential(3, n_samples).astype(int),
        'appearances': np.random.randint(0, 38, n_samples),
        'tier': np.random.choice([1, 2, 3, 4], n_samples, p=[0.4, 0.3, 0.2, 0.1]),
        'contract_years_left': np.random.uniform(0.5, 5.0, n_samples)
    }
    
    # Adjust stats based on position
    df = pd.DataFrame(data)
    df.loc[df['position'] == 'Defender', 'goals'] = (df.loc[df['position'] == 'Defender', 'goals'] * 0.2).astype(int)
    df.loc[df['position'] == 'Goalkeeper', 'goals'] = 0
    df.loc[df['position'] == 'Goalkeeper', 'assists'] = 0
    
    df['minutes_played'] = df['appearances'] * np.random.uniform(60, 90, n_samples)
    df['market_value_m'] = simulate_market_value(df)
    
    df['goal_contribution'] = df['goals'] + df['assists']
    df['mins_per_appearance'] = np.where(df['appearances'] > 0, df['minutes_played'] / df['appearances'], 0)
    
    return df

def simulate_market_value(df):
    """Generates a pseudo-realistic market value in millions based on stats and age."""
    base_value = 1.0
    
    # Age factor: peak value around 24-27
    age_factor = np.where(df['age'] < 22, 1.5, 
                 np.where(df['age'] <= 28, 2.0, 
                 np.where(df['age'] <= 32, 1.0, 0.4)))
                 
    # Performance factor
    perf = (df['goals'] * 2.5) + (df['assists'] * 1.5) + (df['appearances'] * 0.5)
    
    # Noise for market unpredictability
    noise = np.random.lognormal(0, 0.5, len(df))
    
    value = (base_value + perf) * age_factor * noise
    return value.clip(0.1, 200.0)  # Bound between 100k and 200M

def train_valuation_models():
    df = build_valuation_dataset()
    if df is None:
        return
        
    logger.info(f"Dataset shape: {df.shape}")
    
    # Encode Position
    le = LabelEncoder()
    df['position_encoded'] = le.fit_transform(df['position'])
    
    features = ['age', 'position_encoded', 'goals', 'assists', 'appearances', 
                'minutes_played', 'goal_contribution', 'mins_per_appearance',
                'tier', 'contract_years_left']
    
    # Drop rows where target variable is NaN (if Kaggle merge failed on some players)
    df = df.dropna(subset=['market_value_m', 'tier', 'contract_years_left'])
    
    X = df[features]
    y = df['market_value_m']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # --- Baseline: Linear Regression ---
    logger.info("Training baseline Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    
    lr_mae = mean_absolute_error(y_test, lr_preds)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_preds))
    logger.info(f"Linear Regression -> MAE: {lr_mae:.2f}M, RMSE: {lr_rmse:.2f}M")
    
    # --- Advanced: Random Forest Regressor ---
    logger.info("Training Random Forest Regressor...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    
    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
    logger.info(f"Random Forest     -> MAE: {rf_mae:.2f}M, RMSE: {rf_rmse:.2f}M")
    
    # Select Best Model
    best_model = rf if rf_rmse < lr_rmse else lr
    best_name = "RandomForest" if best_model == rf else "LinearRegression"
    best_preds = rf_preds if best_model == rf else lr_preds
    logger.info(f"Winner: {best_name}")
    
    # --- Confidence Range Estimation (using RF variance) ---
    if best_name == "RandomForest":
        # Calculate standard deviation of predictions across all trees in the forest
        tree_preds = np.stack([tree.predict(X_test.values) for tree in rf.estimators_])
        std_dev = np.std(tree_preds, axis=0)
        logger.info(f"Average Model Confidence Range: +/- {np.mean(std_dev):.2f}M")
    
    # Serialize Model & Encoder
    model_dir = "../../models"
    os.makedirs(model_dir, exist_ok=True)
    with open(f'{model_dir}/transfer_value_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    with open(f'{model_dir}/position_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
    logger.info("Model and Encoder serialized.")
    
    # --- Evaluation Charts ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_test, y=best_preds, alpha=0.6, color='#1E90FF')
    # Ideal prediction line
    plt.plot([0, y_test.max()], [0, y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Market Value (€ Millions)')
    plt.ylabel('Predicted Market Value (€ Millions)')
    plt.title(f'Actual vs Predicted Market Value ({best_name})')
    plt.savefig('actual_vs_predicted.png')
    logger.info("Saved actual_vs_predicted.png")
    
    if best_name == "RandomForest":
        plt.figure(figsize=(10, 6))
        importance = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
        sns.barplot(x=importance.values, y=importance.index, palette='viridis')
        plt.title('Feature Importance - Transfer Value Model')
        plt.savefig('feature_importance.png')
        logger.info("Saved feature_importance.png")

if __name__ == "__main__":
    train_valuation_models()
