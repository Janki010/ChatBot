#!/bin/bash

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

API_PORT=${PORT:-8000}
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

echo "Starting FastAPI on port $API_PORT..."

uvicorn main:app \
    --host 0.0.0.0 \
    --port "$API_PORT" &

API_PID=$!

echo "Starting Streamlit on port $STREAMLIT_PORT..."

streamlit run streamlit_app.py \
    --server.address 0.0.0.0 \
    --server.port "$STREAMLIT_PORT" &

STREAMLIT_PID=$!

trap "kill $API_PID $STREAMLIT_PID" SIGINT SIGTERM

wait $API_PID $STREAMLIT_PID