FROM python:3.11
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY ./pipeline /code/pipeline
WORKDIR /code/app
# Create model directory and generate dummy model if needed
RUN mkdir -p saved/challengers
RUN python -c "import pickle; import numpy as np; from sklearn.ensemble import RandomForestRegressor; model = RandomForestRegressor(n_estimators=10, random_state=42); X = np.random.random((100, 10)); y = np.random.random(100); model.fit(X, y); pickle.dump(model, open('saved/challengers/model.pkl', 'wb'))"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
