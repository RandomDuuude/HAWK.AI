import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { uploadImageToServer } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function CameraScreen() {
  const webcamRef = useRef(null);
  const [intervalId, setIntervalId] = useState(null);
  const navigate = useNavigate();

  const captureAndSend = async () => {
    const imageSrc = webcamRef.current.getScreenshot(); // returns data:image/jpeg;base64,...
    if (!imageSrc) return;

    // Remove the "data:image/jpeg;base64," prefix
    const base64 = imageSrc.split(',')[1];

    // Generate a filename using timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `photo_${timestamp}.jpg`;

    // Send to backend
    await uploadImageToServer(base64, filename);
  };

  const startCapturing = () => {
    const id = setInterval(captureAndSend, 5000); // every 5 seconds
    setIntervalId(id);
  };

  const stopCapturing = () => {
    clearInterval(intervalId);
    setIntervalId(null);
  };

  return (
    <div className="p-6">
      <Webcam
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={350}
        audio={false}
      />
      <div className="mt-4 space-x-4">
        <button
          className="bg-green-600 px-4 py-2 text-white rounded"
          onClick={startCapturing}
        >
          Start
        </button>
        <button
          className="bg-red-600 px-4 py-2 text-white rounded"
          onClick={stopCapturing}
        >
          Stop
        </button>
      </div>
      <div className="mt-6 space-x-4">
        <button
          onClick={() => navigate('/lost')}
          className="bg-purple-500 px-4 py-2 text-white rounded"
        >
          Lost and Found
        </button>
        <button
          onClick={() => navigate('/zone')}
          className="bg-yellow-600 px-4 py-2 text-white rounded"
        >
          Zone Density
        </button>
      </div>
    </div>
  );
}
