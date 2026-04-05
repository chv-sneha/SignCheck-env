# SignCheck-env

An OpenEnv-compliant environment simulating an ICU patient scenario where an AI agent acts as a first-responder before the doctor arrives.

## Setup & Running

You can run this project locally using Docker, or run it directly using Python.

### Running with Docker

```bash
docker build -t signcheck-env .
docker run -p 7860:7860 signcheck-env
```

### Running Locally

```bash
pip install -r requirements.txt
uvicorn server.main:app --port 7860
```

### Inference

Once the server is running on `localhost:7860`, set your environment variables:
```bash
export OPENAI_API_KEY=your_key_here
export MODEL_NAME=gpt-4o # Or a local model via OpenAI compatible endpoint
```

Then run the inference script which will sequentially execute all 3 tasks:
```bash
python inference.py
```
