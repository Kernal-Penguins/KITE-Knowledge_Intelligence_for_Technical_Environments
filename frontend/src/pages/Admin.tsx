import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle } from 'lucide-react';
import { api, ROUTES } from "../lib/api";

const Admin = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus('idle');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    try {

      const res = await api.post(
        ROUTES.ingest,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      const data = res.data;

      setStatus('success');
      setMessage(`Job ID: ${data.job_id} is processing in the background.`);
      setFile(null);
    } catch (err: any) {
      setStatus('error');
      const errorMsg = err.response?.data?.detail || err.message || "Upload failed";
      setMessage(errorMsg);
    }
  };

  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <SettingsIcon className="text-gray-400" />
            Admin Data Ingestion
          </h1>
          <p className="text-gray-400 mt-2">Upload Markdown maintenance logs, SOPs, or P&ID images to the ingestion pipeline.</p>
        </div>

        <div className="bg-gray-900 border-2 border-dashed border-gray-700 rounded-xl p-12 text-center transition-colors hover:border-gray-500">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".md,.pdf,.png,.jpg,.jpeg"
          />

          <div className="mx-auto w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mb-4">
            <Upload className="text-gray-400 w-8 h-8" />
          </div>

          <h3 className="text-lg font-medium text-white mb-2">Drag & Drop or Click to Upload</h3>
          <p className="text-sm text-gray-500 mb-6">Supports .md, .pdf, .png, .jpg (Max 50MB)</p>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Select File
          </button>

          {file && (
            <div className="mt-8 bg-gray-800 p-4 rounded-lg flex items-center justify-between text-left border border-gray-700">
              <div className="flex items-center gap-3">
                <FileText className="text-blue-400" />
                <div>
                  <p className="text-white font-medium text-sm">{file.name}</p>
                  <p className="text-gray-400 text-xs">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <button
                onClick={handleUpload}
                disabled={status === 'uploading'}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                {status === 'uploading' ? 'Uploading...' : 'Confirm Upload'}
              </button>
            </div>
          )}
        </div>

        {status === 'success' && (
          <div className="bg-emerald-900/20 border border-emerald-500/50 rounded-xl p-6 text-emerald-200 flex gap-3">
            <CheckCircle className="flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-emerald-400">Upload Successful</h3>
              <p className="text-sm mt-1">{message}</p>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-red-200 flex gap-3">
            <AlertTriangle className="flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-red-400">Upload Failed</h3>
              <p className="text-sm mt-1">{message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const SettingsIcon = (props: any) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" /><circle cx="12" cy="12" r="3" /></svg>
)

export default Admin;