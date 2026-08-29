FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend and python code
COPY . .

# Generate the initial database, synthetic data, and train models at build time
RUN python data/generate_data.py
RUN python db/database.py
RUN python ml/train_models.py

EXPOSE 8000

# Run FastAPI Server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
