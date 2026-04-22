import React, { useState, useEffect, useRef } from "react";
import { Upload, FileText, Trash2, Loader2, CheckCircle, AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { uploadDocument, listDocuments, deleteDocument } from "../api";
import "./Sidebar.css";

function Sidebar({ refreshKey, onUploadComplete, documents, setDocuments }) {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [collapsed, setCollapsed] = useState(false);
  const fileInputRef = useRef(null);

  const fetchDocuments = async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      await uploadDocument(file);
      setUploadStatus({ type: "success", message: `${file.name} uploaded and processed` });
      onUploadComplete();
    } catch (err) {
      setUploadStatus({ type: "error", message: err.message });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Delete "${filename}"? This will remove the document and all its data.`)) return;

    try {
      await deleteDocument(docId);
      onUploadComplete();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className={`sidebar ${collapsed ? "sidebar--collapsed" : ""}`}>
      <button className="sidebar__toggle" onClick={() => setCollapsed(!collapsed)}>
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      {!collapsed && (
        <>
          <div className="sidebar__header">
            <div className="sidebar__logo">
              <div className="sidebar__logo-icon">T</div>
              <div>
                <h1 className="sidebar__title">ThinkDocs</h1>
                <p className="sidebar__subtitle">AI Document Q&A</p>
              </div>
            </div>
          </div>

          <div className="sidebar__upload">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              ref={fileInputRef}
              className="sidebar__file-input"
              disabled={uploading}
            />
            <button
              className="sidebar__upload-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <Loader2 size={18} className="spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Upload size={18} />
                  <span>Upload PDF</span>
                </>
              )}
            </button>

            {uploadStatus && (
              <div className={`sidebar__status sidebar__status--${uploadStatus.type}`}>
                {uploadStatus.type === "success" ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
                <span>{uploadStatus.message}</span>
              </div>
            )}
          </div>

          <div className="sidebar__documents">
            <h3 className="sidebar__section-title">
              Documents ({documents.length})
            </h3>

            {documents.length === 0 ? (
              <div className="sidebar__empty">
                <FileText size={32} strokeWidth={1} />
                <p>No documents uploaded yet</p>
                <p className="sidebar__empty-hint">Upload a PDF to get started</p>
              </div>
            ) : (
              <div className="sidebar__doc-list">
                {documents.map((doc) => (
                  <div key={doc.id} className="sidebar__doc-item">
                    <div className="sidebar__doc-info">
                      <FileText size={16} className="sidebar__doc-icon" />
                      <div className="sidebar__doc-details">
                        <p className="sidebar__doc-name" title={doc.original_filename}>
                          {doc.original_filename}
                        </p>
                        <p className="sidebar__doc-meta">
                          {formatFileSize(doc.file_size)} · {doc.page_count} pages · {doc.chunk_count} chunks
                        </p>
                      </div>
                    </div>
                    <div className="sidebar__doc-actions">
                      <span className={`sidebar__doc-status sidebar__doc-status--${doc.status}`}>
                        {doc.status}
                      </span>
                      <button
                        className="sidebar__delete-btn"
                        onClick={() => handleDelete(doc.id, doc.original_filename)}
                        title="Delete document"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Sidebar;