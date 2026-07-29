import React, { useState } from 'react';

export default function ImageUploader({ onUpload, title, description, accept = "image/*", isMultiple = false }) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(isMultiple ? e.dataTransfer.files : e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(isMultiple ? e.target.files : e.target.files[0]);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      className={`glass-panel p-10 rounded-2xl border-2 border-dashed text-center transition-all cursor-pointer ${
        dragActive
          ? 'border-cyan-400 bg-cyan-950/20'
          : 'border-slate-800 hover:border-slate-700 hover:bg-slate-900/40'
      }`}
    >
      <input
        type="file"
        accept={accept}
        multiple={isMultiple}
        onChange={handleChange}
        className="hidden"
        id="file-upload"
      />
      <label htmlFor="file-upload" className="cursor-pointer space-y-4 inline-block">
        <div className="w-16 h-16 mx-auto rounded-full bg-slate-900 flex items-center justify-center border border-slate-800 text-cyan-400">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-100">{title || "Upload Media File"}</h3>
          <p className="text-sm text-slate-400 mt-1">{description || "Drag & drop file here or click to browse"}</p>
        </div>
        <div className="pt-2">
          <span className="gradient-btn px-5 py-2.5 rounded-xl text-sm font-bold text-white inline-block shadow-md">
            Select File
          </span>
        </div>
      </label>
    </div>
  );
}
