import { useRef } from "react";
import { Upload } from "lucide-react";

interface Props {
  accept?: string;
  label?: string;
  onChange: (file: File) => void;
  disabled?: boolean;
}

export default function FileUpload({ accept, label = "Choose file", onChange, disabled }: Props) {
  const ref = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onChange(file);
  };

  return (
    <div>
      <input ref={ref} type="file" accept={accept} onChange={handleChange} className="hidden" disabled={disabled} />
      <button
        type="button"
        onClick={() => ref.current?.click()}
        disabled={disabled}
        className="btn-secondary"
      >
        <Upload className="h-4 w-4" />
        {label}
      </button>
    </div>
  );
}
