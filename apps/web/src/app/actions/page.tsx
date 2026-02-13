import { fetchJSON } from "@/lib/api";
import ActionsList from "@/components/ActionsList";

interface RemediationAction {
  id: string;
  finding_id: string;
  action_type: string;
  status: string;
  title: string;
  description?: string;
  params: any;
  result?: any;
  error_message?: string;
  proposed_at: string;
  approved_at?: string;
  approved_by?: string;
}

export default async function ActionsPage() {
  const actions = await fetchJSON<RemediationAction[]>("/actions/");

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Remediation Actions</h1>
      <p className="text-gray-600 mb-8">
        Review and approve proposed remediation actions detected by the system.
      </p>
      
      <ActionsList actions={actions} />
    </div>
  );
}
