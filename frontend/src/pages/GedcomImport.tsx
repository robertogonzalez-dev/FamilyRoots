import { useState } from "react";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import { gedcomService } from "../services/gedcomService";
import FileUpload from "../components/FileUpload";
import LoadingSpinner from "../components/LoadingSpinner";

interface ImportResult {
  persons_created: number;
  persons_skipped: number;
  relationships_created: number;
  errors: string[];
}

export default function GedcomImport() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setResult(null);
  };

  const handleImport = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await gedcomService.importFile(selectedFile);
      setResult(data.result);
      toast.success("GEDCOM import complete!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? "Import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Import GEDCOM</h1>
        <p className="text-gray-500">Upload a .ged file exported from Ancestry.com or any genealogy software.</p>
      </div>

      <div className="card space-y-4">
        <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center space-y-3">
          <Upload className="h-10 w-10 text-gray-300 mx-auto" />
          <p className="text-gray-500 text-sm">Select a GEDCOM (.ged) file to upload</p>
          <FileUpload
            accept=".ged,.gedcom"
            label={selectedFile ? selectedFile.name : "Choose GEDCOM file"}
            onChange={handleFileSelect}
            disabled={loading}
          />
          {selectedFile && (
            <p className="text-xs text-gray-400">{(selectedFile.size / 1024).toFixed(1)} KB</p>
          )}
        </div>

        <button
          onClick={handleImport}
          disabled={!selectedFile || loading}
          className="btn-primary w-full"
        >
          {loading ? <LoadingSpinner size="sm" /> : <Upload className="h-4 w-4" />}
          {loading ? "Importing..." : "Import GEDCOM"}
        </button>
      </div>

      {result && (
        <div className="card space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Import Complete
          </h2>
          <dl className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-green-50 rounded-lg p-3">
              <dt className="text-xs text-gray-500">Created</dt>
              <dd className="text-2xl font-bold text-green-700">{result.persons_created}</dd>
              <dd className="text-xs text-gray-500">people</dd>
            </div>
            <div className="bg-yellow-50 rounded-lg p-3">
              <dt className="text-xs text-gray-500">Skipped</dt>
              <dd className="text-2xl font-bold text-yellow-700">{result.persons_skipped}</dd>
              <dd className="text-xs text-gray-500">duplicates</dd>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <dt className="text-xs text-gray-500">Relationships</dt>
              <dd className="text-2xl font-bold text-blue-700">{result.relationships_created}</dd>
              <dd className="text-xs text-gray-500">created</dd>
            </div>
          </dl>
          {result.errors.length > 0 && (
            <div>
              <p className="text-sm font-medium text-red-600 flex items-center gap-1 mb-2">
                <AlertCircle className="h-4 w-4" />
                {result.errors.length} warnings
              </p>
              <ul className="space-y-1">
                {result.errors.map((e, i) => (
                  <li key={i} className="text-xs text-red-500 bg-red-50 rounded px-2 py-1">{e}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
