import React, { useState } from 'react';

export default function ProcessForm({ docId }) {
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleProcess = async () => {
    setError('');
    try {
      const res = await fetch('http://localhost:8000/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: docId }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold">Process Document</h2>
      <p>Document ID: <code>{docId}</code></p>
      <button
        onClick={handleProcess}
        className="mt-2 px-4 py-2 bg-green-600 text-white rounded"
      >
        Start Processing
      </button>
      {error && <p className="text-red-600 mt-2">{error}</p>}
      {result && (
        <div className="mt-4">
          <h3 className="font-medium">Result:</h3>
          <pre className="bg-gray-100 p-2 rounded">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
