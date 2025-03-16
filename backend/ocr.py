import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import os
import easyocr

def extract_text_from_image(image_bytes: bytes, filename: str = "") -> str:
    """
    Extracts text from file bytes using OCR.
    
    For PDFs:
      - Converts each page of the PDF to an image at a high DPI (e.g., 400 DPI).
      - Uses EasyOCR to extract text from each image.
      - Combines the text from all pages.
      
    For non-PDF images:
      - Decodes the image using OpenCV.
      - Converts the image to grayscale and applies adaptive thresholding.
      - Uses Tesseract OCR to extract text.
    
    Returns:
      A string containing the concatenated OCR text.
    """
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    
    if ext == ".pdf":
        try:
            # Convert PDF pages to images at high DPI for improved resolution.
            pages = convert_from_bytes(image_bytes, dpi=400)
            texts = []
            # Initialize EasyOCR reader for English (set gpu=True if a GPU is available)
            reader = easyocr.Reader(['en'], gpu=False)
            for i, page in enumerate(pages):
                # pdf2image produces a PIL image in RGB mode.
                img = np.array(page)
                # EasyOCR expects an RGB image.
                results = reader.readtext(img, detail=0, paragraph=True)
                page_text = " ".join(results)
                texts.append(page_text)
                print(f"[INFO] Processed page {i+1} of PDF '{filename}' using EasyOCR.")
            all_text = "\n".join(texts)
            if not all_text.strip():
                print(f"[WARN] No text extracted from PDF '{filename}'.")
            return all_text
        except Exception as e:
            err_msg = f"Error processing PDF '{filename}' with EasyOCR: {e}"
            print(err_msg)
            return err_msg
    else:
        try:
            # Decode the image from bytes.
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                err_msg = "Unsupported or corrupted image file."
                print(err_msg)
                return err_msg
            
            # Convert to grayscale.
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Apply adaptive thresholding to handle uneven lighting.
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
            # Run Tesseract OCR with advanced configuration.
            text = pytesseract.image_to_string(thresh, lang="eng", config="--oem 5 --psm 11")
            if not text.strip():
                print(f"[WARN] No text extracted from image '{filename}'.")
            return text
        except Exception as e:
            err_msg = f"Error processing image '{filename}': {e}"
            print(err_msg)
            return err_msg
