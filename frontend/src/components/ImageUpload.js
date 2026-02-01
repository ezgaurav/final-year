import React, { useRef } from 'react';
import api from '../services/api';

const ImageUpload = ({ onResults, onLoading }) => {
  const fileInputRef = useRef(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    onLoading(true);
    try {
      const response = await api.detectMedicine(file);
      if (response.success) {
        onResults([response.medicine_info]);
      } else {
        alert(response.message || 'Could not detect medicine. Try searching manually.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading image. Please try again.');
    } finally {
      onLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="image-upload">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="image/*"
        style={{ display: 'none' }}
      />
      <button onClick={handleButtonClick} className="upload-button">
        📷 Upload Image
      </button>
    </div>
  );
};

export default ImageUpload;
