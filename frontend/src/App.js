import logo from './logo.svg';
import './App.css';
import UploadForm from "./components/UploadForm";
import ProcessForm from "./components/ProcessForm";
import { useState } from "react";

function App() {
  const [docId, setDocId] = useState('');
  return (
    <div className="App">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Document Processing UI</h1>
        <UploadForm onUpload={(id) => setDocId(id)} />
        {docId && <ProcessForm docId={docId} />}
      </div>
    </div>
  );
}

export default App;
