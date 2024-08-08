let cameraStarted = false;
let currentStream = null;

document.addEventListener('DOMContentLoaded', initializeCamera);

async function initializeCamera() {
    const startCameraButton = document.getElementById('start-camera');
    const cameraSelect = document.getElementById('camera-select');
    const captureButton = document.getElementById('capture');
    const videoElement = document.getElementById('camera-stream');
    const resultDiv = document.getElementById('result');

    await populateCameraSelect();
    startCameraButton.addEventListener('click', toggleCamera);
    cameraSelect.addEventListener('change', () => startCamera(true));
    captureButton.addEventListener('click', captureImage);
}

async function populateCameraSelect() {
    const cameras = await getCameras();
    const select = document.getElementById('camera-select');
    select.innerHTML = '';
    cameras.forEach((camera, index) => {
        const option = document.createElement('option');
        option.value = camera.deviceId;
        option.text = camera.label || `Camera ${index + 1}`;
        select.appendChild(option);
    });
    select.style.display = cameras.length > 1 ? 'block' : 'none';
}

async function getCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter(device => device.kind === 'videoinput');
    } catch (err) {
        console.error("Eroare la enumerarea dispozitivelor:", err);
        return [];
    }
}

async function toggleCamera() {
    const startCameraButton = document.getElementById('start-camera');
    const videoElement = document.getElementById('camera-stream');
    const captureButton = document.getElementById('capture');

    if (!cameraStarted) {
        try {
            await startCamera();
            startCameraButton.textContent = 'Oprește Camera';
            cameraStarted = true;
        } catch (err) {
            console.error("Eroare la pornirea camerei:", err);
            alert("Eroare la pornirea camerei. Vă rugăm să verificați permisiunile.");
        }
    } else {
        stopCamera();
        startCameraButton.textContent = 'Pornește Camera';
        cameraStarted = false;
    }
}

async function startCamera(isChangeEvent = false) {
    if (currentStream) {
        stopCamera();
    }

    const selectedCamera = document.getElementById('camera-select').value;
    const constraints = {
        video: { 
            deviceId: selectedCamera ? { exact: selectedCamera } : undefined,
            facingMode: selectedCamera ? undefined : "environment"
        }
    };

    try {
        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        const videoElement = document.getElementById('camera-stream');
        videoElement.srcObject = currentStream;
        videoElement.style.display = 'block';
        document.getElementById('capture').disabled = false;

        if (!isChangeEvent) {
            document.getElementById('start-camera').textContent = 'Oprește Camera';
            cameraStarted = true;
        }
    } catch (err) {
        console.error("Eroare la pornirea camerei:", err);
        handleCameraError(err);
    }
}

function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    const videoElement = document.getElementById('camera-stream');
    videoElement.srcObject = null;
    videoElement.style.display = 'none';
    document.getElementById('capture').disabled = true;
}

function handleCameraError(error) {
    console.error('Camera error:', error);
    let errorMessage;
    switch(error.name) {
        case 'NotAllowedError':
            errorMessage = 'Acces la cameră refuzat. Vă rugăm să acordați permisiunea în setările browserului.';
            break;
        case 'NotFoundError':
            errorMessage = 'Nu s-a găsit nicio cameră pe dispozitiv.';
            break;
        case 'NotReadableError':
            errorMessage = 'Camera nu poate fi accesată. Încercați să reporniți dispozitivul.';
            break;
        case 'OverconstrainedError':
            errorMessage = 'Nicio cameră disponibilă nu îndeplinește cerințele specificate.';
            break;
        case 'AbortError':
            errorMessage = 'Accesul la cameră a fost întrerupt.';
            break;
        default:
            errorMessage = `Eroare necunoscută la accesarea camerei: ${error.message}`;
    }
    alert(errorMessage);
    document.getElementById('result').textContent = errorMessage;
}

function captureImage() {
    if (!currentStream) {
        alert("Vă rugăm să porniți mai întâi camera.");
        return;
    }

    const videoElement = document.getElementById('camera-stream');
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    canvas.getContext('2d').drawImage(videoElement, 0, 0);
    const imageData = canvas.toDataURL('image/png');

    fetch('/process_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerHTML = `Eroare: ${data.error}`;
        } else {
            const resultHtml = `
                <h2>Rezultate:</h2>
                <p>Dimensiuni: Lungime - ${data.dimensions.length}cm, Lățime - ${data.dimensions.width}cm, Înălțime - ${data.dimensions.height}cm</p>
                <h3>Imagine Originală cu Contururi:</h3>
                <img src="${data.processed_image}" alt="Imagine procesată" style="max-width: 100%;">
            `;
            document.getElementById('result').innerHTML = resultHtml;
        }
    })
    .catch(error => {
        console.error('Eroare:', error);
        document.getElementById('result').innerHTML = 'A apărut o eroare la procesarea imaginii.';
    });
}