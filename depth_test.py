import cv2
import numpy as np
from primesense import openni2
import os

# ==============================================================================
# CONFIGURATION FOR RASPBERRY PI
# ==============================================================================
# On Raspberry Pi (Debian/Raspbian), installing 'libopenni2-0' via apt 
# usually places the libraries in /usr/lib/OpenNI2 or /usr/lib/aarch64-linux-gnu/OpenNI2
# We will try to auto-detect, but you can hardcode it if needed.

# Default path for apt-get installed OpenNI2 on many Linux systems
OPENNI2_DIR = "/usr/lib/OpenNI2" 

# If you downloaded a specific SDK (like Orbbec OpenNI2 SDK for ARM),
# point this to the folder containing 'libOpenNI2.so' and the 'Drivers' folder.
# OPENNI2_DIR = "/home/pi/OpenNI2/Redist" 
# ==============================================================================

def main():
    # 1. Initialize OpenNI2
    try:
        # Check if the directory exists, otherwise try initializing without path (system default)
        if os.path.exists(OPENNI2_DIR):
            openni2.initialize(OPENNI2_DIR)
            print(f"OpenNI2 Initialized from: {OPENNI2_DIR}")
        else:
            print(f"Path {OPENNI2_DIR} not found. Trying system default initialization...")
            openni2.initialize() # Try finding it in system PATH
            print("OpenNI2 Initialized from system path.")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize OpenNI2.")
        print(f"Details: {e}")
        print("Ensure you ran: sudo apt install libopenni2-0 libopenni2-dev")
        return

    # 2. Open the Device
    try:
        dev = openni2.Device.open_any()
        print(f"Device Opened: {dev.get_device_info()}")
    except Exception as e:
        print(f"\n[ERROR] Could not open device.")
        print(f"Details: {e}")
        print("troubleshooting:")
        print("1. Did you unplug/replug the camera after setting udev rules?")
        print("2. Try running with 'sudo python3 script.py' to check if it's a permission issue.")
        openni2.unload()
        return

    # 3. Create Depth Stream
    depth_stream = dev.create_depth_stream()
    depth_stream.start()
    print("Depth stream started...")
    
    # 4. Set Video Mode (Optional but recommended for Pi performance)
    # 320x240 @ 30 FPS is faster on Pi than 640x480
    try:
        depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX=320, resolutionY=240, fps=30))
    except:
        pass # If mode not supported, ignore

    try:
        while True:
            # 5. Read Frame
            frame = depth_stream.read_frame()
            frame_data = frame.get_buffer_as_uint16()
            
            # 6. Convert to Numpy Array
            h, w = frame.height, frame.width
            depth_array = np.frombuffer(frame_data, dtype=np.uint16)
            depth_array = depth_array.reshape((h, w))

            # 7. Normalize and Visualize
            # Normalize to 0-255. We cap max distance at 3000mm (3 meters) for better contrast
            # Anything beyond 3 meters becomes pure white (255)
            depth_image = cv2.normalize(depth_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            # Color map (Jet is good, but try PLASMA for a modern look)
            depth_colormap = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

            cv2.imshow('Astra Depth (Press q to exit)', depth_colormap)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        # 8. Cleanup
        print("Stopping stream and unloading OpenNI2...")
        depth_stream.stop()
        openni2.unload()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()