import api from "./api";

interface ImportResult {
  message: string;
  result: {
    persons_created: number;
    persons_skipped: number;
    relationships_created: number;
    errors: string[];
  };
}

export const gedcomService = {
  async importFile(file: File): Promise<ImportResult> {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post<ImportResult>("/gedcom/import", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
};
