# WordSnap API

Backend aplikacji WordSnap do rozpoznawania fiszek ze zdjęć.

## Opis

WordSnap to API, które umożliwia przesyłanie zdjęć zawierających słówka i ich tłumaczenia, a następnie zwraca je w formie JSON-a z fiszkami.

## Wymagania

- Python 3.9+
- Tesseract OCR

## Instalacja Tesseract OCR

### Windows
1. Pobierz instalator z [oficjalnej strony](https://github.com/UB-Mannheim/tesseract/wiki)
2. Zainstaluj i dodaj ścieżkę do zmiennych środowiskowych

### Linux (Ubuntu/Debian)
```
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-pol tesseract-ocr-eng
```

### MacOS
```
brew install tesseract
brew install tesseract-lang
```

## Instalacja i uruchomienie

1. Klonuj repozytorium
2. Utwórz wirtualne środowisko: `python -m venv venv`
3. Aktywuj środowisko:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Zainstaluj zależności: `pip install -r requirements.txt`
5. Uruchom serwer: `uvicorn main:app --reload`

API będzie dostępne pod adresem: http://127.0.0.1:8000

## Endpointy

- `GET /` - Informacje o API
- `POST /upload-photo` - Przesyłanie zdjęcia z fiszkami

## Przykład użycia

```python
import requests

url = "http://127.0.0.1:8000/upload-photo"
files = {"image": open("fiszki.jpg", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

## Deployment na Render.com

Projekt zawiera plik `render.yaml`, który umożliwia automatyczny deployment na Render.com.

1. Połącz repozytorium z Render.com
2. Skonfiguruj nową usługę Web Service
3. Render automatycznie wykryje konfigurację z pliku render.yaml 