import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SignIn() {
  const [name, setName] = useState('');
  const [volunteerId, setVolunteerId] = useState('');
  const navigate = useNavigate();

  const handleSignIn = () => {
    if (!name || !volunteerId) return alert("Enter name and ID");
    localStorage.setItem('volunteer', JSON.stringify({ name, volunteerId }));
    navigate('/camera');
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl mb-4">Volunteer Sign In</h1>
      <input className="border p-2 mb-2 block w-full" placeholder="Name" onChange={e => setName(e.target.value)} />
      <input className="border p-2 mb-4 block w-full" placeholder="Volunteer ID" onChange={e => setVolunteerId(e.target.value)} />
      <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={handleSignIn}>Sign In</button>
    </div>
  );
}
