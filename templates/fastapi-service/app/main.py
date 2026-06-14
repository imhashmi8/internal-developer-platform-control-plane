from fastapi import FastAPI

app = FastAPI(title="{{ service_name }}")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "{{ service_name }}"}
