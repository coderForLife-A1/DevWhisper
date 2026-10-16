



from fastapi import FastAPI, File, UploadFile
from pydantic import ValidationError
from fastapi.responses import JSONResponse
import os
from transcriber import AudioTranscriber
from extractor import process_transcript




app = FastAPI()
@app.post("/api/process")
async def process_audio(file: UploadFile = File(...)):

    try:





        with open(f"temp_{file.filename}", "wb") as buffer:
            buffer.write(await file.read())

        audio = AudioTranscriber(model_name="base.en").transcribe(f"temp_{file.filename}")
        extracted_data = process_transcript(audio)
        
        return {
            "status": "success",

            "transcript": audio,
            "data": extracted_data.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(f"temp_{file.filename}"):
            os.remove(f"temp_{file.filename}")
