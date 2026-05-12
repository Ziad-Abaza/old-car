from flask import Flask, Response, render_template_string
import cv2
import time

app = Flask(__name__)

# Initialize the camera (0 is usually the default USB cam)
camera = cv2.VideoCapture(0)

# Set resolution (optional, lower resolution = higher FPS)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    prev_frame_time = 0
    new_frame_time = 0

    while True:
        # Read the camera frame
        success, frame = camera.read()
        if not success:
            break
        
        # --- FPS Calculation ---
        new_frame_time = time.time()
        # Calculate FPS = 1 / (time taken to process frame)
        # We add 0.00001 to avoid division by zero errors
        fps = 1 / ((new_frame_time - prev_frame_time) + 0.00001)
        prev_frame_time = new_frame_time
        
        # Convert FPS to integer string
        fps_text = f"FPS: {int(fps)}"

        # --- Draw FPS on Frame ---
        # Arguments: image, text, position, font, scale, color (B,G,R), thickness
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2, cv2.LINE_AA)

        # --- Encode Frame to JPEG ---
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame in the format required for a multipart stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    # Simple inline HTML to display the video feed
    return render_template_string('''
        <html>
            <head>
                <title>Pi Camera Stream</title>
                <style>
                    body { text-align: center; background-color: #222; color: white; font-family: sans-serif; }
                    h1 { margin-top: 20px; }
                    img { border: 5px solid #444; border-radius: 4px; }
                </style>
            </head>
            <body>
                <h1>Live Camera Feed</h1>
                <img src="{{ url_for('video_feed') }}" width="640">
            </body>
        </html>
    ''')

@app.route('/video_feed')
def video_feed():
    # Return the response generated along with the specific media type (mime type)
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # host='0.0.0.0' allows access from other devices on the network
    # port=5000 is the default port
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        camera.release() # Release camera on exit