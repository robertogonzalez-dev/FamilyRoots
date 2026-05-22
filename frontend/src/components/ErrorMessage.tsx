import { AlertCircle } from "lucide-react";

interface Props {
  message: string;
  className?: string;
}

export default function ErrorMessage({ message, className = "" }: Props) {
  return (
    <div className={`flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 ${className}`}>
      <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
      <p className="text-sm text-red-700">{message}</p>
    </div>
  );
}
