// src/components/ZoneDensity.jsx
import React, { useEffect, useState } from 'react';

export default function ZoneDensity() {
  const [zones, setZones] = useState([
    { zone: 'A', count: 40 },
    { zone: 'B', count: 120 }, // This will trigger alert
  ]);

  useEffect(() => {
    zones.forEach(z => {
      if (z.count > 100) {
        alert(`⚠️ High crowd in zone ${z.zone}: ${z.count} people`);
      }
    });
  }, [zones]);

  return (
    <div className="p-6">
      <h2 className="text-xl mb-4">Zone Density Monitor</h2>
      <div className="grid grid-cols-2 gap-4">
        {zones.map((z, i) => (
          <div key={i} className={`p-4 border rounded shadow ${z.count > 100 ? 'bg-red-200' : 'bg-green-100'}`}>
            <h3 className="font-bold">Zone {z.zone}</h3>
            <p>People: {z.count}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
