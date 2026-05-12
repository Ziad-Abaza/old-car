import cv2
from pyzbar.pyzbar import decode
import WebcamModule as wM

# Main loop
while True:
    # Capture frame from camera
    frame = wM.getImg(True, size=[224, 224])
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Decode QR codes
    qr_codes = decode(gray)
    
    # Process detected QR codes
    for qr_code in qr_codes:
        # Extract QR code data
        qr_data = qr_code.data.decode('utf-8')
        
        # Draw bounding box around QR code
        (x, y, w, h) = qr_code.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Display QR code data
        cv2.putText(frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Print QR code data (for debugging)
        print(f'QR Code detected: {qr_data}')
    
    # Display the frame
    cv2.imshow('QR Code Scanner', frame)
    
    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
