import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import PersonForm from "../components/PersonForm";
import { peopleService } from "../services/peopleService";
import type { PersonCreate } from "../types/person";
import { apiErrorMessage } from "../utils/errors";

export default function AddPerson() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data: PersonCreate) => {
    setLoading(true);
    try {
      const person = await peopleService.create(data);
      toast.success("Person added successfully");
      navigate(`/people/${person.id}`);
    } catch (err) {
      toast.error(apiErrorMessage(err, "Failed to add person"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Add Person</h1>
        <p className="text-gray-500">Create a new family member record.</p>
      </div>
      <div className="card">
        <PersonForm onSubmit={handleSubmit} submitLabel="Add Person" loading={loading} />
      </div>
    </div>
  );
}
