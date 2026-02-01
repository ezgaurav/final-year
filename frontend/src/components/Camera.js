import React, { useRef, useState } from 'react';
import api from '../services/api';

const Camera = ({ onResults, onLoading }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [stream, setStream] = useState(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' } // Use back camera on mobile
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
        setStream(mediaStream);
        setIsStreaming(true);
      }
    } catch (error) {
      console.error('Camera error:', error);
      alert('Could not access camera. Please grant camera permissions.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsStreaming(false);
    }
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Set canvas dimensions to video dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to blob
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      
      // Create file from blob
      const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
      
      onLoading(true);
      try {
        const response = await api.processCameraImage(file);
        if (response.success) {
          onResults([response.medicine_info]);
          stopCamera();
        } else {
          alert(response.message || 'Could not detect medicine. Try again or use search.');
        }
      } catch (error) {
        console.error('Camera capture error:', error);
        alert('Error processing image. Please try again.');
      } finally {
        onLoading(false);
      }
    }, 'image/jpeg', 0.95);
  };

  return (
    <div className="camera">
      {!isStreaming ? (
        <button onClick={startCamera} className="camera-button">
          📸 Use Camera
        </button>
      ) : (
        <div className="camera-container">
          <video ref={videoRef} className="camera-video" />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div className="camera-controls">
            <button onClick={capturePhoto} className="capture-button">
              📸 Capture
            </button>
            <button onClick={stopCamera} className="stop-button">
              ✖ Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Camera;
