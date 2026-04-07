# Hugging Face Space Deployment

Use a Docker Space for this repo.

## What Is Already Ready

* `README.md` has Hugging Face Space metadata
* `Dockerfile` exposes port `8000`
* FastAPI app serves:
  * `GET /health`
  * `GET /metadata`
  * `POST /reset`
  * `POST /step`

## What To Do On Hugging Face

1. Create a new Space
2. Choose `Docker` as the SDK
3. Push this repo to the Space

## After Deploy

Check these URLs:

* `/health`
* `/metadata`
* `/docs`

Then test:

* `POST /reset`
* `POST /step`

## Local Notes

If Docker is installed locally, verify with:

```bash
docker build -t geo-audit-env .
docker run -p 8000:8000 geo-audit-env
```
