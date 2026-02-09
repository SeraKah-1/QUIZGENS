"use client";

import { useState } from "react";
import { api } from "@/lib/api"; // <--- PERBAIKAN: Pakai 'api', bukan 'uploadApi'
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UploadCloud, Loader2, FileText, X } from "lucide-react";
import { toast } from "sonner";
import { AxiosError } from "axios";

interface Props {
  onSuccess: (jobId: string) => void;
  isLoading: boolean;
}

export function FileUploader({ onSuccess, isLoading }: Props) {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return toast.error("Pilih file dulu!");
    
    // Validasi Ukuran (Max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      return toast.error("File terlalu besar! Maksimal 5MB.");
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("amount", "5"); // Default jumlah soal

    try {
      // PERBAIKAN: Gunakan 'api.post' dengan header multipart
      const res = await api.post("/api/v1/quiz/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      toast.success("File berhasil diupload!");
      onSuccess(res.data.job_id); // Kirim ID ke parent untuk polling status
    } catch (e) {
      const error = e as AxiosError;
      console.error("Upload Error:", error);
      toast.error("Gagal Upload: " + (error.message || "Server Error"));
    }
  };

  return (
    <div className="space-y-4 animate-in fade-in">
      <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center space-y-4 hover:bg-slate-50 transition-colors">
        
        {!file ? (
          <>
            <div className="mx-auto w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
              <UploadCloud size={24} />
            </div>
            <div>
              <Label htmlFor="file-upload" className="cursor-pointer text-blue-600 font-semibold hover:underline">
                Klik untuk upload PDF/MD
              </Label>
              <Input 
                id="file-upload" 
                type="file" 
                accept=".pdf,.md,.txt" 
                className="hidden" 
                onChange={handleFileChange}
                disabled={isLoading}
              />
              <p className="text-xs text-slate-400 mt-2">Maksimal 5MB</p>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center gap-3">
              <div className="bg-red-100 text-red-600 p-2 rounded">
                <FileText size={20} />
              </div>
              <div className="text-left">
                <p className="text-sm font-medium truncate max-w-[200px]">{file.name}</p>
                <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setFile(null)} disabled={isLoading}>
              <X size={18} className="text-slate-400" />
            </Button>
          </div>
        )}

      </div>

      <Button onClick={handleUpload} disabled={isLoading || !file} className="w-full">
        {isLoading ? <Loader2 className="animate-spin mr-2" /> : null}
        {isLoading ? "Memproses AI..." : "Upload & Generate Kuis"}
      </Button>
    </div>
  );
}