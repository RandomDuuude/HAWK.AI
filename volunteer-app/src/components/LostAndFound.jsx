import React, { useState } from 'react';
import axios from 'axios';
import { sendLostFoundQuery } from '../services/api';

export default function LostAndFound() {
  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [langCode, setLangCode] = useState('hi-IN');
  const [isListening, setIsListening] = useState(false); // 🔊 mic status

  const translateToEnglish = async (text) => {
  try {
    const res = await axios.post('https://translate.argosopentech.com/translate', {
      q: text,
      source: 'auto',
      target: 'en',
      format: 'text'
    }, {
      headers: { 'Content-Type': 'application/json' }
    });

    console.log("Original:", text, "| Translated:", res.data.translatedText);
    return res.data.translatedText;
  } catch (err) {
    console.error("Translation Error:", err.response?.data || err.message);
    alert("Translation failed, using original text.");
    return text;
  }
};

  const startSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech Recognition not supported in this browser');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = langCode;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    setIsListening(true); // 🔴 Start loader

    recognition.onresult = async (event) => {
      const spokenText = event.results[0][0].transcript;
      console.log("Spoken Text:", spokenText);

      const translated = await translateToEnglish(spokenText);
      setName(translated);
      setIsListening(false); // 🟢 Stop loader
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      alert('Speech recognition error: ' + event.error);
      setIsListening(false); // 🟢 Stop loader on error
    };

    recognition.onend = () => {
      setIsListening(false); // 🔚 Stop loader when done
    };

    recognition.start();
  };

  const handleSubmit = async () => {
    if (!name || !file) {
      alert("Please enter a name and upload a photo");
      return;
    }

    try {
      const res = await sendLostFoundQuery(name, file);
      setResult(res);
    } catch (err) {
      console.error("Lost and Found API Error:", err.message);
      alert("Search failed");
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Lost and Found Query</h2>

      <div className="mb-4">
        <label className="mr-2 font-medium">Choose Language:</label>
        <select
          value={langCode}
          onChange={(e) => setLangCode(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="hi-IN">Hindi</option>
          <option value="bn-IN">Bengali</option>
          <option value="ta-IN">Tamil</option>
          <option value="te-IN">Telugu</option>
          <option value="mr-IN">Marathi</option>
          <option value="gu-IN">Gujarati</option>
          <option value="kn-IN">Kannada</option>
          <option value="ml-IN">Malayalam</option>
          <option value="ur-IN">Urdu</option>
        </select>
      </div>

      <div className="flex items-center mb-4">
        <input
          type="text"
          className="border p-2 flex-grow"
          placeholder="Translated Name in English"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button
          onClick={startSpeechRecognition}
          className={`ml-2 p-2 rounded transition duration-300 ${
            isListening ? 'bg-red-300 animate-pulse' : 'bg-gray-200 hover:bg-gray-300'
          }`}
          title="Speak in selected language"
        >
          {isListening ? '🎙️ Listening...' : '🎤 Speak'}
        </button>
      </div>

      <input
        className="mb-4"
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        onClick={handleSubmit}
      >
        Search
      </button>

      {result && (
        <div className="mt-4">
          <p className="font-bold">Match Found:</p>
          <img src={result.imageURL} alt="Match" className="w-64 mt-2 border" />
        </div>
      )}
    </div>
  );
}
