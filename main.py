from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import easyocr
import tempfile
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = easyocr.Reader(['en'], gpu=False)

@app.post("/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    allergens: str = Form("")
):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(await file.read())
    temp.close()

    result = reader.readtext(temp.name, detail=0)
    ocr_text = " ".join(result).lower()

    allergen_list = [a.strip().lower() for a in allergens.split(",") if a.strip()]
    found_allergens = [a for a in allergen_list if a in ocr_text]

    return {
        "text": ocr_text,
        "found_allergens": found_allergens,
        "has_allergens": len(found_allergens) > 0
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
