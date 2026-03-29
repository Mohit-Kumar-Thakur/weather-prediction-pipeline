import joblib
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from ml_data import load_historical_data, create_features, prepare_training_data


# ─────────────────────────────────────────
# Step 1: Evaluate a model and print metrics
# ─────────────────────────────────────────
def evaluate_model(model_name, y_test, y_pred):
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    print(f"\n{model_name} Results:")
    print(f"  RMSE : {rmse:.2f} °C")
    print(f"  MAE  : {mae:.2f} °C")
    print(f"  R²   : {r2:.4f}")
    return rmse, mae, r2


# ─────────────────────────────────────────
# Step 2: Train all models and compare
# ─────────────────────────────────────────
def train_models(X_train, X_test, y_train, y_test):
    models = {
        "Linear Regression" : LinearRegression(),
        "Random Forest"     : RandomForestRegressor(
                                n_estimators=100,
                                random_state=42
                              ),
        "XGBoost"           : XGBRegressor(
                                n_estimators=200,
                                learning_rate=0.1,
                                max_depth=6,
                                random_state=42,
                                verbosity=0
                              )
    }

    results = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse, mae, r2 = evaluate_model(name, y_test, y_pred)
        results[name] = {
            "model" : model,
            "rmse"  : rmse,
            "mae"   : mae,
            "r2"    : r2
        }

    return results


# ─────────────────────────────────────────
# Step 3: Pick the best model by RMSE
# ─────────────────────────────────────────
def get_best_model(results):
    best_name = min(results, key=lambda x: results[x]["rmse"])
    best      = results[best_name]
    print(f"\nBest model: {best_name}")
    print(f"  RMSE : {best['rmse']:.2f} °C")
    print(f"  MAE  : {best['mae']:.2f} °C")
    print(f"  R²   : {best['r2']:.4f}")
    return best_name, best["model"]


# ─────────────────────────────────────────
# Step 4: Save the best model to disk
# ─────────────────────────────────────────
def save_model(model, feature_columns, path="ml_model.pkl"):
    joblib.dump({
        "model"           : model,
        "feature_columns" : feature_columns
    }, path)
    print(f"\nModel saved to {path}")


# ─────────────────────────────────────────
# Step 5: Plot actual vs predicted
# ─────────────────────────────────────────
def plot_predictions(y_test, y_pred, model_name):
    plt.figure(figsize=(14, 5))

    plt.subplot(1, 2, 1)
    plt.plot(y_test.values[:168], label="Actual",    color="blue",  linewidth=1)
    plt.plot(y_pred[:168],        label="Predicted", color="orange", linewidth=1)
    plt.title(f"{model_name} — Actual vs Predicted (first 7 days)")
    plt.xlabel("Hour")
    plt.ylabel("Temperature (°C)")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.scatter(y_test, y_pred, alpha=0.3, color="teal", s=5)
    plt.plot(
        [y_test.min(), y_test.max()],
        [y_test.min(), y_test.max()],
        color="red", linewidth=1
    )
    plt.title(f"{model_name} — Actual vs Predicted scatter")
    plt.xlabel("Actual Temperature (°C)")
    plt.ylabel("Predicted Temperature (°C)")

    plt.tight_layout()
    plt.savefig("prediction_plot.png", dpi=150)
    plt.show()
    print("Plot saved to prediction_plot.png")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Training started...")
    print("=" * 50)

    # load and prepare data
    df_raw      = load_historical_data()
    df_featured = create_features(df_raw)
    X_train, X_test, y_train, y_test = prepare_training_data(df_featured)

    feature_columns = list(X_train.columns)

    # train all models
    print("\nTraining 3 models...")
    results = train_models(X_train, X_test, y_train, y_test)

    # pick best
    best_name, best_model = get_best_model(results)

    # save best model
    save_model(best_model, feature_columns)

    # plot predictions
    y_pred = best_model.predict(X_test)
    plot_predictions(y_test, y_pred, best_name)

    print("\n" + "=" * 50)
    print("Training complete!")
    print("=" * 50)