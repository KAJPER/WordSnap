from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import re

app = FastAPI(title="WordSnap API")

# Dodanie CORS middleware, aby umożliwić zapytania z aplikacji mobilnej
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Witaj w API WordSnap. Użyj /upload-photo, aby przesłać zdjęcie."}

@app.post("/upload-photo")
async def upload_photo(image: UploadFile = File(...)):
    # Sprawdzenie typu pliku
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Przesłany plik nie jest obrazem")
    
    try:
        # Odczytanie obrazu
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        # Wykonanie OCR
        text = pytesseract.image_to_string(img, lang='pol+eng')
        
        # Przetworzenie tekstu na fiszki
        flashcards = parse_text_to_flashcards(text)
        
        return {"flashcards": flashcards}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania obrazu: {str(e)}")

def parse_text_to_flashcards(text):
    flashcards = []
    
    # Podział na linie
    lines = text.strip().split("\n")
    
    for line in lines:
        # Usunięcie pustych linii
        if not line.strip():
            continue
        
        # Dopasowanie wzorców: "słowo - tłumaczenie" lub "słowo – tłumaczenie"
        match = re.split(r'\s+[-–]\s+', line, maxsplit=1)
        
        if len(match) == 2:
            word = match[0].strip()
            translation = match[1].strip()
            
            # Dodawanie tylko niepustych par
            if word and translation:
                flashcards.append({
                    "word": word,
                    "translation": translation
                })
    
    return flashcards

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 