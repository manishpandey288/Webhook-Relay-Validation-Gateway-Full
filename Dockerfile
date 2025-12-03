# Use Python 3.11 so pydantic-core wheels exist (no Rust compile)
FROM python:3.11-slim

# avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# copy and install requirements first (faster rebuilds)
COPY requirements.txt .

# upgrade installers and install requirements
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# copy the rest of the code
COPY . .

# expose port (Railway uses $PORT, but this is the container port)
EXPOSE 8000

# default start command; change main:app if your FastAPI app is in another file or named differently
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
