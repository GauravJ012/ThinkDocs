import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import "./App.css";

function App() {
  const [documents, setDocuments] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadComplete = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="app-layout">
      <Sidebar
        refreshKey={refreshKey}
        onUploadComplete={handleUploadComplete}
        documents={documents}
        setDocuments={setDocuments}
      />
      <ChatPanel documents={documents} />
    </div>
  );
}

export default App;