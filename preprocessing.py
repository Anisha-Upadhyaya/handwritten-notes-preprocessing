import os
import shutil
import cv2
import numpy as np
from pdf2image import convert_from_path

POPPLER_PATH = r"C:\Users\anushka\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

os.makedirs("uploaded", exist_ok=True)
os.makedirs("processed", exist_ok=True)

file_path = input("Enter the full path of the PDF or image file (must be upright): ").strip()

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

uploaded_path = os.path.join("uploaded", os.path.basename(file_path))
shutil.copy(file_path, uploaded_path)
print(f"File copied: {uploaded_path}")

image_exts = ('.png', '.jpg', '.jpeg')
pdf_exts = ('.pdf',)

#preprocessing
def preprocess_image(img):
    #grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Denoise 
    denoised = cv2.medianBlur(gray, 3)

    #Adaptive Threshold
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 35, 15
    )

    #Morphological opening
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    #contour filtering
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 1 < area < 15:   
            cv2.drawContours(clean, [cnt], -1, (255, 255, 255), -1)

    #sharpening
    sharpen_kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]])
    final = cv2.filter2D(clean, -1, sharpen_kernel)

    return final



#File Handling
#PDF
if file_path.lower().endswith(pdf_exts):
    print("PDF detected. Converting pages to images...")
    pages = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
    for i, page in enumerate(pages):
        page_path = os.path.join("processed", f"page_{i+1}.png")
        page.save(page_path, 'PNG')

        img = cv2.imread(page_path)
        processed_img = preprocess_image(img)

        processed_path = os.path.join("processed", f"page_{i+1}_processed.png")
        cv2.imwrite(processed_path, processed_img)
        print(f"Saved: {processed_path}")

#Img
elif file_path.lower().endswith(image_exts):
    print("Image detected. Processing...")
    img = cv2.imread(file_path)
    processed_img = preprocess_image(img)

    processed_path = os.path.join(
        "processed", f"{os.path.splitext(os.path.basename(file_path))[0]}_processed.png")
    cv2.imwrite(processed_path, processed_img)
    print(f"Saved: {processed_path}")

else:
    print("Unsupported file format. Please upload PDF, PNG, JPG, or JPEG.")
