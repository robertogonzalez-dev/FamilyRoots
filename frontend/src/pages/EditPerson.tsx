import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import PersonForm from "../components/PersonForm";
import LoadingSpinner from "../components/LoadingSpinner";
import { peopleService } from "../services/peopleService";
import type { Person, PersonCreate } from "../types/person";

export default function EditPerson() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [person, setPerson] = useState<Person | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    peopleService.get(Number(id))
      .then(setPerson)
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (data: PersonCreate) => {
    if (!person) return;
    setSaving(true);
    try {
      await peopleService.update(person.id, data);
      toast.success("Person updated");
      navigate(`/people/${person.id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? "Failed to update person");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="py-24" />;
  if (!person) return <p className="text-gray-500">Person not found.</p>;

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Edit Person</h1>
        <p className="text-gray-500">{person.full_name}</p>
      </div>
      <div className="card">
        <PersonForm
          defaultValues={person}
          onSubmit={handleSubmit}
          submitLabel="Save Changes"
          loading={saving}
        />
      </div>
    </div>
  );
}
