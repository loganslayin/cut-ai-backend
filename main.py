from fastapi import FastAPI, File, UploadFile, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import shutil
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.mount("/videos", StaticFiles(directory="videos"), name="videos")
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logging.debug(f"Uploaded file saved at: {file_location}")
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(os.getcwd(), "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/edit/trim")
async def trim_video(
    filename: str = Query(...),
    start: float = Query(...),
    end: float = Query(...)
):
    logging.debug(f"Received trim request: filename={filename}, start={start}, end={end}")

    input_path = os.path.join(UPLOAD_DIR, filename)
    output_path = os.path.join(UPLOAD_DIR, f"trimmed_{filename}")

    if not os.path.exists(input_path):
        logging.error(f"File not found: {input_path}")
        return {"error": "File not found"}

    if start < 0 or end <= start:
        logging.error(f"Invalid start or end time: start={start}, end={end}")
        return {"error": "Invalid start or end time"}

    try:
        command = [
            "ffmpeg",
            "-y",  # overwrite output file if exists
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",  # copy codecs (fast, no re-encode)
            output_path
        ]
        logging.debug(f"Running ffmpeg command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"ffmpeg error: {result.stderr}")
            return {"error": f"Trimming failed: {result.stderr}"}

    except Exception as e:
        logging.error(f"Trimming failed: {e}")
        return {"error": f"Trimming failed: {str(e)}"}

    logging.debug(f"Trimmed video saved to {output_path}")
    return {"trimmed_video": f"/videos/trimmed_{filename}"}
