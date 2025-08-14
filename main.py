from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import tempfile
import os

app = FastAPI()

# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    allergens: str = Form("")
):
    # Save the uploaded file temporarily
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(await file.read())
    temp.close()

    # Open image and run OCR
    img = Image.open(temp.name)
    ocr_text = pytesseract.image_to_string(img).lower()

    # Check for allergens
    allergen_list = [a.strip().lower() for a in allergens.split(",") if a.strip()]
    found_allergens = [a for a in allergen_list if a in ocr_text]

    # Return results
    return {
        "text": ocr_text,
        "found_allergens": found_allergens,
        "has_allergens": len(found_allergens) > 0
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
