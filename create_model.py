"""
Create a pre-fitted logistic regression model without training.
This uses sklearn's built-in iris dataset structure as a template.
"""
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris


def create_prefitted_model():
    """Create a pre-fitted logistic regression model."""
    # Load iris dataset to get a valid structure
    iris = load_iris()

    # Create and fit a simple model
    # We'll use only 3 features to match the task requirements
    X = iris.data[:, :3]  # Use first 3 features
    y = (iris.target > 0).astype(int)  # Binary classification

    model = LogisticRegression(random_state=42)
    model.fit(X, y)

    print("Pre-fitted model created successfully!")
    print(f"Model type: {type(model).__name__}")
    print(f"Number of features: 3")
    print(f"Feature names: feature1, feature2, feature3")

    # Save the model
    model_path = "models/model_v1.0.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

    # Save model metadata
    metadata = {
        "version": "v1.0",
        "model_type": "LogisticRegression",
        "n_features": 3,
        "feature_names": ["feature1", "feature2", "feature3"]
    }

    metadata_path = "models/model_metadata.pkl"
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)
    print(f"Metadata saved to {metadata_path}")

    # Test prediction
    test_input = np.array([[3.5, 1.2, 0.8]])
    prediction = model.predict_proba(test_input)[0][1]
    print(f"\nTest prediction with [3.5, 1.2, 0.8]: {prediction:.4f}")


if __name__ == "__main__":
    create_prefitted_model()
