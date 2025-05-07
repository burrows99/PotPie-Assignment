import React, { useState } from 'react';

export default function UploadForm({ onUpload }) {
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState('{}');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!file) {
      setError('Please select a file');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', metadata);

      const res = await fetch('https://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      onUpload(data.id);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div>
        <label className="block font-medium">Select Document:</label>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="mt-1"
        />
      </div>
      <div className="mt-4">
        <label className="block font-medium">Metadata (JSON):</label>
        <textarea
          value={metadata}
          onChange={(e) => setMetadata(e.target.value)}
          rows={3}
          className="w-full border p-2"
        />
      </div>
      {error && <p className="text-red-600 mt-2">{error}</p>}
      <button
        type="submit"
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Upload
      </button>
    </form>
  );
}