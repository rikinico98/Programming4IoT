import cv2
from pyzbar.pyzbar import decode

def readBarcode():
    image = cv2.imread(r'barcode.png')
    detectedBarcodes = decode(image)
    for barcode in detectedBarcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)
        return (barcode.data)

