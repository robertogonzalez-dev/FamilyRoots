import { useForm } from "react-hook-form";
import type { PersonCreate } from "../types/person";

interface Props {
  defaultValues?: Partial<PersonCreate>;
  onSubmit: (data: PersonCreate) => Promise<void>;
  submitLabel?: string;
  loading?: boolean;
}

export default function PersonForm({ defaultValues, onSubmit, submitLabel = "Save", loading }: Props) {
  const { register, handleSubmit } = useForm<PersonCreate>({
    defaultValues: defaultValues ?? {},
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="label">First Name</label>
          <input {...register("first_name")} className="input" placeholder="John" />
        </div>
        <div>
          <label className="label">Middle Name</label>
          <input {...register("middle_name")} className="input" placeholder="William" />
        </div>
        <div>
          <label className="label">Last Name</label>
          <input {...register("last_name")} className="input" placeholder="Smith" />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Maiden Name</label>
          <input {...register("maiden_name")} className="input" placeholder="Jones" />
        </div>
        <div>
          <label className="label">Gender</label>
          <select {...register("gender")} className="input">
            <option value="unknown">Unknown</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Birth Date</label>
          <input {...register("birth_date")} type="date" className="input" />
        </div>
        <div>
          <label className="label">Birth Place</label>
          <input {...register("birth_place")} className="input" placeholder="City, Country" />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Death Date</label>
          <input {...register("death_date")} type="date" className="input" />
        </div>
        <div>
          <label className="label">Death Place</label>
          <input {...register("death_place")} className="input" placeholder="City, Country" />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input {...register("is_living")} type="checkbox" id="is_living" className="rounded border-gray-300" />
        <label htmlFor="is_living" className="text-sm font-medium text-gray-700">Person is living</label>
      </div>

      <div>
        <label className="label">Biography</label>
        <textarea {...register("biography")} rows={4} className="input resize-none" placeholder="Short biography..." />
      </div>

      <div className="flex justify-end">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
