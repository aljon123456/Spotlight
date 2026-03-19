import React, { useState } from 'react';
import './FileUpload.css';

const FileUpload = ({ onUploadComplete, uploadType = 'profile' }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const getUploadConfig = () => {
    switch (uploadType) {
      case 'profile':
        return {
          endpoint: '/uploads/upload_profile_picture/',
          acceptTypes: 'image/jpeg,image/png',
          label: 'Upload Profile Picture',
          maxSize: 5242880, // 5MB
          icon: '📸'
        };
      case 'document':
        return {
          endpoint: '/uploads/upload_schedule_document/',
          acceptTypes: '.pdf,image/jpeg,image/png',
          label: 'Upload Schedule Document',
          maxSize: 5242880, // 5MB
          icon: '📄'
        };
      default:
        return {};
    }
  };

  const config = getUploadConfig();

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size
    if (file.size > config.maxSize) {
      setError(`File size exceeds ${config.maxSize / 1024 / 1024}MB limit`);
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Create preview for images
    if (uploadType === 'profile') {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', selectedFile);

    // Add schedule_id if uploading document
    if (uploadType === 'document' && document.querySelector('[name="scheduleId"]')) {
      formData.append('schedule_id', document.querySelector('[name="scheduleId"]').value);
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api${config.endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Upload failed');
      }

      const data = await response.json();
      setUploadProgress(100);
      
      // Call callback with uploaded URL
      if (onUploadComplete) {
        onUploadComplete(data.url);
      }

      // Reset form
      setTimeout(() => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setUploadProgress(0);
      }, 1500);
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDragDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      // Manually create FileList-like object
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      handleFileSelect({ target: { files: dataTransfer.files } });
    }
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-box">
        <div 
          className="file-upload-area"
          onDragOver={(e) => e.preventDefault()}
          onDragLeave={(e) => e.preventDefault()}
          onDrop={handleDragDrop}
        >
          {previewUrl && uploadType === 'profile' ? (
            <img src={previewUrl} alt="Preview" className="file-preview" />
          ) : (
            <>
              <div className="upload-icon">{config.icon}</div>
              <p className="upload-label">{config.label}</p>
              <p className="upload-hint">or drag and drop</p>
            </>
          )}
        </div>

        {selectedFile && (
          <div className="file-info">
            <p className="file-name">
              <strong>Selected:</strong> {selectedFile.name}
            </p>
            <p className="file-size">
              <strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}

        {error && (
          <div className="upload-error">
            <span>⚠️</span> {error}
          </div>
        )}

        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <span className="progress-text">{uploadProgress}%</span>
          </div>
        )}

        {uploadProgress === 100 && (
          <div className="upload-success">
            <span>✅</span> Upload successful!
          </div>
        )}

        <div className="file-upload-controls">
          <label className="file-input-label">
            <input
              type="file"
              accept={config.acceptTypes}
              onChange={handleFileSelect}
              disabled={uploading}
              className="file-input"
            />
            Browse Files
          </label>

          {selectedFile && (
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={uploading || !selectedFile}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          )}
        </div>

        <p className="upload-note">
          Maximum file size: {config.maxSize / 1024 / 1024}MB
        </p>
      </div>
    </div>
  );
};

export default FileUpload;
