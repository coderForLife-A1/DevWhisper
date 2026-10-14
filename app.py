# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from transcriber import AudioTranscriber
from extractor import process_transcript

app = FastAPI(title="DevWhisper Local API")
transcriber = AudioTranscriber(model_name="base.en")

@app.post("/api/process")
async def process_audio(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        transcript = transcriber.transcribe(temp_path)
        extracted_data = process_transcript(transcript)
        
        return {
            "status": "success",
            "transcript": transcript,
            "data": extracted_data.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)