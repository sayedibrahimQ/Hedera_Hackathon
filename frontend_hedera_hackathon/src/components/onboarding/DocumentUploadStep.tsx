'use client';

import { Dispatch, SetStateAction, useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle, FileText, UploadCloud, XCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

type FileState = {
  companyRegistration: File | null;
  businessPlan: File | null;
  financialReport: File | null;
};

type DocumentUploadStepProps = {
  files: FileState;
  setFiles: Dispatch<SetStateAction<FileState>>;
};

export function DocumentUploadStep({ files, setFiles }: DocumentUploadStepProps) {
  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-primary mb-2">Upload Your Documents</h2>
        <p className="text-muted-foreground">Provide these documents to help us and investors understand your business.</p>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <DocumentUploader
          title="Company Registration"
          file={files.companyRegistration}
          setFile={(file) => setFiles((prev) => ({ ...prev, companyRegistration: file }))}
        />
        <DocumentUploader
          title="Business Plan"
          file={files.businessPlan}
          setFile={(file) => setFiles((prev) => ({ ...prev, businessPlan: file }))}
        />
        <DocumentUploader
          title="Financial Report"
          file={files.financialReport}
          setFile={(file) => setFiles((prev) => ({ ...prev, financialReport: file }))}
        />
      </div>
    </div>
  );
}

type DocumentUploaderProps = {
  title: string;
  file: File | null;
  setFile: (file: File | null) => void;
};

function DocumentUploader({ title, file, setFile }: DocumentUploaderProps) {
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const currentFile = acceptedFiles[0];
      setFile(currentFile);
      // Simulate upload progress
      setProgress(0);
      const timer = setInterval(() => {
        setProgress((oldProgress) => {
          if (oldProgress === 100) {
            clearInterval(timer);
            return 100;
          }
          const diff = Math.random() * 10;
          return Math.min(oldProgress + diff, 100);
        });
      }, 50);
    }
  }, [setFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/msword': ['.doc'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    multiple: false,
  });

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setProgress(0);
  };

  return (
    <Card {...getRootProps()} className={cn("text-center p-4 cursor-pointer hover:border-primary transition-colors", isDragActive && "border-primary bg-primary/5")}>
      <input {...getInputProps()} />
      <CardContent className="p-0">
        {!file ? (
          <div className="flex flex-col items-center justify-center h-full">
            <UploadCloud className="w-10 h-10 text-muted-foreground mb-2" />
            <h3 className="font-semibold">{title}</h3>
            <p className="text-xs text-muted-foreground">
              {isDragActive ? 'Drop here...' : 'Drag & drop or click'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="relative">
                <FileText className="w-10 h-10 text-primary mb-2" />
                <button onClick={removeFile} className="absolute -top-2 -right-2 bg-background rounded-full">
                    <XCircle className="w-5 h-5 text-destructive hover:text-destructive/80"/>
                </button>
            </div>
            <p className="text-sm font-medium truncate w-full px-2">{file.name}</p>
            <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(2)} KB</p>
            {progress < 100 ? (
                <Progress value={progress} className="h-2 w-full" />
            ) : (
                <div className="flex items-center text-green-600">
                    <CheckCircle className="w-4 h-4 mr-1"/>
                    <span className="text-xs font-medium">Uploaded</span>
                </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
