import pickle
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor

# Create a simple dummy model
model = RandomForestRegressor(n_estimators=10, random_state=42)

# Create some dummy training data (this would normally come from your pipeline)
X_dummy = np.random.random((100, 10))  # 100 samples, 10 features
y_dummy = np.random.random(100)  # 100 target values

# Train the dummy model
model.fit(X_dummy, y_dummy)

# Ensure directory exists
save_path = "saved/challengers/model.pkl"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the model
with open(save_path, 'wb') as f:
    pickle.dump(model, f)

print("Dummy model created and saved successfully!")
print(f"Model saved to: {save_path}")
print(f"File exists: {os.path.exists(save_path)}")
