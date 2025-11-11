import os
import sys
import time
from pathlib import Path
import qrcode
import cv2  
from barcode import Code128
from barcode.writer import ImageWriter
try:
    from pyzbar.pyzbar import decode as zbar_decode
    _BARCODE_DECODE_AVAILABLE = True
except Exception:
    _BARCODE_DECODE_AVAILABLE = False

OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)

def send_qr(text: str) -> Path:
   
    ts = int(time.time())
    file_path = OUT_DIR / f"qr_{ts}.png"
    img = qrcode.make(text)
    img.save(file_path)
    return file_path

def receive_qr_from_image(image_path: str) -> str | None:
    
    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image. Check path.")
        return None
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)
    if points is None or not data:
        return None
    return data

def receive_qr_from_webcam(camera_index: int = 0):
    
    detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Could not open webcam.")
        return
    print("Show a QR code to the camera. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        data, points, _ = detector.detectAndDecode(frame)
        if points is not None and data:
           
            pts = points[0].astype(int)
            for i in range(len(pts)):
                cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1) % len(pts)]), (0, 255, 0), 2)
            cv2.putText(frame, data, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
            print("Decoded:", data)
        cv2.imshow("QR Receiver", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def send_barcode(text: str) -> Path:
   
    ts = int(time.time())
    file_path = OUT_DIR / f"barcode_{ts}"
   
    barcode = Code128(text, writer=ImageWriter())
    final_path = Path(barcode.save(str(file_path)))  
    return final_path

def receive_barcode_from_image(image_path: str) -> str | None:
   
    if not _BARCODE_DECODE_AVAILABLE:
        print("Barcode decoding is disabled (pyzbar/zbar not installed). See README or install zbar + pyzbar.")
        return None
    import PIL.Image as Image
    try:
        img = Image.open(image_path)
    except Exception:
        print("Could not open image. Check path.")
        return None
    results = zbar_decode(img)
    if not results:
        return None
   
    return results[0].data.decode("utf-8", errors="replace")

def menu():
    print("\n=== QR & Barcode Communication ===")
    print("1) Send message as QR")
    print("2) Receive message from QR image")
    print("3) Receive message from QR via webcam")
    print("4) Send message as Barcode (Code128)")
    print("5) Receive message from Barcode image")
    print("0) Exit")

def main():
    while True:
        menu()
        choice = input("Choose: ").strip()
        if choice == "1":
            text = input("Enter message to send: ")
            path = send_qr(text)
            print(f"Saved QR to: {path}")
        elif choice == "2":
            p = input("Enter QR image path: ").strip().strip('"')
            data = receive_qr_from_image(p)
            if data:
                print("Received message:", data)
            else:
                print("No QR detected / couldn't decode.")
        elif choice == "3":
            receive_qr_from_webcam()
        elif choice == "4":
            text = input("Enter message to send: ")
            path = send_barcode(text)
            print(f"Saved Barcode to: {path}")
        elif choice == "5":
            p = input("Enter Barcode image path: ").strip().strip('"')
            data = receive_barcode_from_image(p)
            if data:
                print("Received message:", data)
            else:
                print("No barcode detected / couldn't decode.")
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
