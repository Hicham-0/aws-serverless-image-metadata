// Configuration

const API_BASE = 'https://#redacted#/prod';
const UPLOAD_ENDPOINT = 'https://#redacted#/prod/upload';
const RESULTS_ENDPOINT = 'https://#redacted#/prod/result';


// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const metadata = document.getElementById('metadata');
const errorMsg = document.getElementById('errorMsg');
const successMsg = document.getElementById('successMsg');
const preview = document.getElementById('preview');

let selectedFile = null;

// Upload area click to select file
uploadArea.addEventListener('click', () => fileInput.click());

// File input change
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFileSelect(file);
    } else {
        showError('Please drop an image file');
    }
});

function handleFileSelect(file) {
    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB');
        return;
    }

    selectedFile = file;
    uploadBtn.disabled = false;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.innerHTML = `<img src="${e.target.result}" alt="Preview" class="image-preview">`;
    };
    reader.readAsDataURL(file);
    clearMessages();
}


// upload button click 
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    uploadBtn.disabled = true;
    loading.classList.add('show');
    clearMessages();

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('filename', selectedFile.name);

        const response = await fetch(UPLOAD_ENDPOINT, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            showSuccess('Image uploaded successfully! ' );
            
            // Poll for metadata 
            pollMetadata(data.Id );
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    } finally {
        loading.classList.remove('show');
        uploadBtn.disabled = false;
    }
});

function pollMetadata(Id) {
    // Poll to check if metadata is ready
    const maxAttempts = 60; 
    let attempts = 0;

    const interval = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${RESULTS_ENDPOINT}/${Id}`);
            
            if (response.ok) {
                const data = await response.json();
                clearInterval(interval);
                displayMetadata(data);
            } else if (attempts >= maxAttempts) {
                clearInterval(interval);
                showError('Metadata processing timed out. Please try again later.');
            }
        } catch (error) {
            if (attempts >= maxAttempts) {
                clearInterval(interval);
                showError('Failed to fetch metadata');
            }
        }
    }, 2000);
}

function displayMetadata(data) {
    result.classList.add('show');
    uploadArea.style.display = 'none';
    uploadBtn.style.display = 'none';
    preview.innerHTML = '';

    metadata.innerHTML = `
        <h3>Image Metadata</h3>
        <div class="metadata-item">
            <span class="metadata-label">Image ID:</span>
            <span class="metadata-value">${data.Id || 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Filename:</span>
            <span class="metadata-value">${data.filename || 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Size:</span>
            <span class="metadata-value">${formatBytes(data.size) || 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Extension:</span>
            <span class="metadata-value">${data.extension || 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Width:</span>
            <span class="metadata-value">${data.width ? data.width + 'px' : 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Format:</span>
            <span class="metadata-value">${data.format }</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Height:</span>
            <span class="metadata-value">${data.height ? data.height + 'px' : 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">EXIF Data:</span>
            <span class="metadata-value">${formatExif(data.exif)}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Upload Time:</span>
            <span class="metadata-value">${new Date(data.uploadTime).toLocaleString() || 'N/A'}</span>
        </div>
    `;
}

clearBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    result.classList.remove('show');
    uploadArea.style.display = 'block';
    uploadBtn.style.display = 'block';
    uploadBtn.disabled = true;
    preview.innerHTML = '';
    clearMessages();
});

function showError(message) {
    errorMsg.textContent = '❌ ' + message;
    errorMsg.classList.add('show');
}

function showSuccess(message) {
    successMsg.textContent = '✅ ' + message;
    successMsg.classList.add('show');
}

function clearMessages() {
    errorMsg.classList.remove('show');
    successMsg.classList.remove('show');
}

function formatBytes(bytes) {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}







