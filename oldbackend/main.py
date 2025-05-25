from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import re
import numpy as np
import cv2

app = FastAPI(title="WordSnap API")

# Dodanie CORS middleware, aby umożliwić zapytania z aplikacji mobilnej
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfiguracja Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.get("/")
async def root():
    return {"message": "Witaj w API WordSnap. Użyj /upload-photo, aby przesłać zdjęcie."}

def preprocess_image(img):
    """
    Przygotowuje obraz do lepszego rozpoznawania tekstu
    """
    # Konwersja do OpenCV
    open_cv_image = np.array(img) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() # Konwersja RGB do BGR
    
    # Konwersja do skali szarości
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    
    # Usunięcie szumu
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Adaptacyjne progowanie
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    
    # Dylatacja tekstu
    kernel = np.ones((1, 1), np.uint8)
    img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    
    # Konwersja z powrotem do PIL
    return Image.fromarray(img_dilation)

@app.post("/upload-photo")
async def upload_photo(image: UploadFile = File(...)):
    # Sprawdzenie typu pliku
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Przesłany plik nie jest obrazem")
    
    try:
        # Odczytanie obrazu
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        # Preprocessing obrazu
        processed_img = preprocess_image(img)
        
        # Konfiguracja Tesseract
        custom_config = r'--oem 3 --psm 6 -l eng+pol'
        
        # Wykonanie OCR
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        
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