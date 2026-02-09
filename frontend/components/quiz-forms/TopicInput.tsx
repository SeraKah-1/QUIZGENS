"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Type, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Props {
  onSuccess: (jobId: string) => void;
  isLoading: boolean;
}

export function TopicInput({ onSuccess, isLoading }: Props) {
  const [topic, setTopic] = useState("");
  const [amountStr, setAmountStr] = useState("5");

  // 👇 GANTI INI DENGAN LINK KOYEB KAMU YANG ASLI (JANGAN PAKAI LOCALHOST)
  // Contoh: "https://nama-app-kamu.koyeb.app"
  const BASE_URL = "https://defeated-marya-farrel2008-b39f2824.koyeb.app"; 

  const handleSubmit = async () => {
    if (!topic.trim()) return toast.error("Isi topik dulu!");
    const finalAmount = parseInt(amountStr) || 5;

    // Kita pakai FETCH bawaan javascript (Tanpa Axios)
    try {
      // Gabungkan URL secara manual biar yakin benar
      const url = `${BASE_URL}/api/v1/quiz/topic`;
      console.log("Mencoba request ke:", url); // Cek console browser nanti

      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic,
          amount: finalAmount,
        }),
      });

      // Fetch tidak otomatis error kalau 404/500, jadi kita cek manual
      if (!res.ok) {
        if (res.status === 404) throw new Error("Alamat URL Salah (404)");
        if (res.status === 422) throw new Error("Data tidak valid (422)");
        if (res.status === 500) throw new Error("Server Error (500)");
        throw new Error(`Gagal: ${res.statusText}`);
      }

      const data = await res.json();
      toast.success("Request Berhasil!");
      onSuccess(data.job_id);

    } catch (error: any) {
      console.error("Fetch Error:", error);
      toast.error(error.message || "Terjadi kesalahan jaringan");
    }
  };

  return (
    <div className="space-y-4 animate-in fade-in">
      <div className="space-y-2">
        <Label>Topik / Materi Teks</Label>
        <Textarea 
            placeholder="Misal: Sejarah Perang Dunia II..." 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)} 
            className="min-h-[100px]"
            disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <Label>Jumlah Soal</Label>
        <Input 
          type="number" 
          value={amountStr} 
          onChange={(e) => setAmountStr(e.target.value)} 
          min={1} max={50}
          disabled={isLoading}
        />
      </div>

      <Button onClick={handleSubmit} disabled={isLoading || !topic} className="w-full">
        {isLoading ? <Loader2 className="animate-spin mr-2"/> : <Type className="mr-2"/>}
        Buat Kuis (Pakai Fetch)
      </Button>
    </div>
  );
}