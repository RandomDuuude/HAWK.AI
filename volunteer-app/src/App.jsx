import React from 'react';
import { Routes, Route } from 'react-router-dom';

import SignIn from './components/SignIn';
import CameraScreen from './components/CameraScreen';
import LostAndFound from './components/LostAndFound';
import ZoneDensity from './components/ZoneDensity';

function App() {
  return (
    <div>
      <h2>Volunteer App</h2>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/camera" element={<CameraScreen />} />
        <Route path="/lost" element={<LostAndFound />} />
        <Route path="/zone" element={<ZoneDensity />} />
      </Routes>
    </div>
  );
}


export default App;
