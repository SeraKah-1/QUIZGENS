"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, UploadCloud, Type } from "lucide-react";

// Import komponen yang sudah kita pisah
import { FileUploader } from "@/components/quiz-forms/FileUploader";
import { TopicInput } from "@/components/quiz-forms/TopicInput";

export default function Home() {
  const [mode, setMode] = useState<"file" | "topic">("file");
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [quizData, setQuizData] = useState<any>(null);

  // --- Logic Polling (Status Checker) ---
  const startPolling = (jobId: string) => {
    setIsLoading(true);
    setQuizData(null);
    setProgress(10);
    toast.info("AI sedang bekerja...");

    const check = async () => {
      try {
        const res = await api.get(`/quiz/status/${jobId}`);
        const status = res.data.status;

        if (status === "completed") {
          setQuizData(res.data.data);
          setIsLoading(false);
          setProgress(100);
          toast.success("Selesai!");
        } else if (status === "failed") {
          setIsLoading(false);
          toast.error("Gagal: " + res.data.error);
        } else {
          // Masih processing
          setProgress((prev) => (prev < 90 ? prev + 10 : 90));
          setTimeout(check, 2000); // Cek lagi 2 detik kemudian
        }
      } catch (e) {
        setIsLoading(false);
        toast.error("Gagal cek status");
      }
    };
    check();
  };

  return (
    <main className="min-h-screen bg-slate-50 py-10 px-4 font-sans">
      <div className="max-w-3xl mx-auto space-y-8">
        
        {/* HEADER */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold text-slate-900">QuizGen AI 🚀</h1>
          <p className="text-lg text-slate-600">Buat kuis instan dari materi apa saja.</p>
        </div>

        {/* INPUT CARD */}
        <Card className="shadow-lg bg-white">
          <CardHeader>
            {/* TAB SWITCHER */}
            <div className="flex p-1 bg-slate-100 rounded-lg mb-4">
               <button onClick={() => setMode("file")} className={`flex-1 py-2 text-sm font-medium rounded-md flex items-center justify-center gap-2 transition-all ${mode === 'file' ? 'bg-white shadow text-blue-600' : 'text-slate-500'}`}>
                 <UploadCloud className="w-4 h-4"/> Upload File
               </button>
               <button onClick={() => setMode("topic")} className={`flex-1 py-2 text-sm font-medium rounded-md flex items-center justify-center gap-2 transition-all ${mode === 'topic' ? 'bg-white shadow text-blue-600' : 'text-slate-500'}`}>
                 <Type className="w-4 h-4"/> Tulis Topik
               </button>
            </div>
            <CardTitle>{mode === 'file' ? 'Upload Dokumen' : 'Input Topik Manual'}</CardTitle>
            <CardDescription>Pilih cara input materi kuis kamu.</CardDescription>
          </CardHeader>
          
          <CardContent>
            {/* RENDER KOMPONEN SESUAI MODE */}
            {mode === "file" ? (
              <FileUploader onSuccess={startPolling} isLoading={isLoading} />
            ) : (
              <TopicInput onSuccess={startPolling} isLoading={isLoading} />
            )}

            {isLoading && (
              <div className="mt-4 space-y-2">
                <Progress value={progress} className="h-2" />
                <p className="text-xs text-center text-slate-400">Sedang memproses...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* RESULT CARD */}
        {quizData && (
          <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center gap-2 text-green-600 bg-green-50 p-3 rounded-lg border border-green-200">
              <CheckCircle2 /> <span className="font-bold">Kuis Berhasil Dibuat!</span>
            </div>
            
            {quizData.questions?.map((q: any, idx: number) => (
              <Card key={idx} className="border-l-4 border-l-blue-500">
                <CardHeader><CardTitle>{idx + 1}. {q.question}</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {q.options.map((opt: string, i: number) => (
                      <div key={i} className={`p-2 border rounded ${i === q.answer_index ? 'bg-green-100 border-green-300' : 'bg-slate-50'}`}>
                        {opt}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

      </div>
    </main>
  );
}