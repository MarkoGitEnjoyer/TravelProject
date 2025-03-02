const video = document.getElementById('video');
const previewCanvas = document.getElementById('previewCanvas');
const resultContainer = document.getElementById('resultContainer');
const successDiv = document.getElementById('successMessage');
const errorDiv = document.getElementById('errorMessage');
const userIdSpan = document.getElementById('userIdResult');
const secretKeySpan = document.getElementById('secretKeyResult');
const statusIndicator = document.querySelector('.status-indicator');
const statusText = document.querySelector('.status-text');
let stream;

// Update camera status function
function updateCameraStatus(isActive) {
    if (isActive) {
        statusIndicator.parentElement.classList.add('status-active');
        statusText.textContent = 'Camera on';
    } else {
        statusIndicator.parentElement.classList.remove('status-active');
        statusText.textContent = 'Camera off';
    }
}

// Start Camera
document.getElementById('startButton').addEventListener('click', async () => {
    // If camera is already running, stop it
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        stream = null;
        updateCameraStatus(false);
        return;
    }
    
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        
        // Update the status when camera successfully starts
        updateCameraStatus(true);
        
    } catch (error) {
        alert('Camera error: ' + error.message);
        updateCameraStatus(false);
    }
});

// QR Scanning
document.getElementById('captureButton').addEventListener('click', () => {
    if (!stream) {
        alert('Please start the camera first!');
        return;
    }
    
    // Set canvas dimensions to match video
    previewCanvas.width = video.videoWidth;
    previewCanvas.height = video.videoHeight;
    
    if (previewCanvas.width === 0 || previewCanvas.height === 0) {
        alert('Video dimensions are not ready yet. Please try again in a moment.');
        return;
    }
    
    const ctx = previewCanvas.getContext('2d');
    
    try {
        // Draw video frame to canvas
        ctx.drawImage(video, 0, 0, previewCanvas.width, previewCanvas.height);
        
        // Get image data
        const imageData = ctx.getImageData(0, 0, previewCanvas.width, previewCanvas.height);
        
        // Try to detect QR code directly
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        
        if (code) {
            // QR code found!
            handleQRSuccess(code.data);
            return;
        }
        
        // If direct scan failed, try with rotations
        const rotations = [90, 180, 270]; // Try different rotations
        
        for (const rotation of rotations) {
            try {
                const rotatedData = rotateImageData(imageData, rotation);
                if (!rotatedData || !rotatedData.width) {
                    console.log(`Invalid rotated data for ${rotation}°`);
                    continue;
                }
                
                const rotatedCode = jsQR(rotatedData.data, rotatedData.width, rotatedData.height);
                
                if (rotatedCode) {
                    handleQRSuccess(rotatedCode.data);
                    return;
                }
            } catch (error) {
                console.error(`Rotation error at ${rotation}°:`, error);
            }
        }
        
        // If we got here, no QR code was found
        alert('No QR code detected. Please try again with better lighting or positioning.');
        
    } catch (error) {
        alert('Error processing image: ' + error.message);
    }
});

// Properly implemented rotation function
function rotateImageData(imageData, degrees) {
    if (!imageData || !imageData.width || !imageData.height) {
        console.error('Invalid image data provided to rotation function');
        return null;
    }
    
    const sourceCanvas = document.createElement('canvas');
    sourceCanvas.width = imageData.width;
    sourceCanvas.height = imageData.height;
    const sourceCtx = sourceCanvas.getContext('2d');
    sourceCtx.putImageData(imageData, 0, 0);

    // Create destination canvas with proper dimensions
    const destCanvas = document.createElement('canvas');
    if (degrees === 90 || degrees === 270) {
        destCanvas.width = imageData.height;
        destCanvas.height = imageData.width;
    } else {
        destCanvas.width = imageData.width;
        destCanvas.height = imageData.height;
    }
    
    const destCtx = destCanvas.getContext('2d');
    
    // Translate and rotate
    destCtx.translate(destCanvas.width / 2, destCanvas.height / 2);
    destCtx.rotate(degrees * Math.PI / 180);
    destCtx.translate(-imageData.width / 2, -imageData.height / 2);
    
    // Draw the original image
    destCtx.drawImage(sourceCanvas, 0, 0);
    
    // Return the rotated image data
    return destCtx.getImageData(0, 0, destCanvas.width, destCanvas.height);
}

// Handle successful scan
function handleQRSuccess(data) {
    // Reset previous messages
    successDiv.textContent = '';
    errorDiv.textContent = '';
    resultContainer.style.display = 'block';
    const tripId = document.getElementById('qr-data').getAttribute('data-trip-id');
    console.log('[DEBUG] Sending QR data:', data);
    
    fetch(`/guide/process_qr/${tripId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ qr_data: data })
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.error) {
            errorDiv.textContent = `Error: ${data.error}`;
            console.error('[ERROR] Server response:', data);
        } else {
            successDiv.textContent = '✅ Scan successful!';
            userIdSpan.textContent = data.user_id || 'N/A';
            secretKeySpan.textContent = data.secret_key || 'N/A';
            console.log('[SUCCESS] Server response:', data);
        }
    })
    .catch(error => {
        errorDiv.textContent = `Error: ${error.message}`;
        console.error('[FETCH ERROR]', error);
    });
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize camera status on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set initial camera status
    updateCameraStatus(false);
});