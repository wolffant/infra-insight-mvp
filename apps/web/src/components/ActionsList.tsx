"use client";

import { postJSON } from "@/lib/api";
import { useState } from "react";

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

interface ActionsListProps {
  actions: RemediationAction[];
}

export default function ActionsList({ actions }: ActionsListProps) {
  const [localActions, setLocalActions] = useState(actions);
  const [loading, setLoading] = useState<string | null>(null);

  const handleApprove = async (actionId: string) => {
    setLoading(actionId);
    try {
      const updated = await postJSON<RemediationAction>(
        `/actions/${actionId}/approve`,
        { approved_by: "user" }
      );
      setLocalActions(prev =>
        prev.map(a => a.id === actionId ? updated : a)
      );
    } catch (err) {
      alert("Failed to approve action");
    } finally {
      setLoading(null);
    }
  };

  const handleReject = async (actionId: string) => {
    setLoading(actionId);
    try {
      const updated = await postJSON<RemediationAction>(
        `/actions/${actionId}/reject`,
        { approved_by: "user" }
      );
      setLocalActions(prev =>
        prev.map(a => a.id === actionId ? updated : a)
      );
    } catch (err) {
      alert("Failed to reject action");
    } finally {
      setLoading(null);
    }
  };

  if (localActions.length === 0) {
    return <p className="text-gray-500">No remediation actions proposed yet.</p>;
  }

  return (
    <div className="space-y-4">
      {localActions.map(action => (
        <div key={action.id} className="border rounded-lg p-4 bg-white shadow">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-semibold text-lg">{action.title}</h3>
              {action.description && (
                <p className="text-sm text-gray-600 mt-1">{action.description}</p>
              )}
            </div>
            <StatusBadge status={action.status} />
          </div>

          <div className="mt-3 text-sm text-gray-700">
            <p><strong>Action Type:</strong> {action.action_type}</p>
            <p><strong>Proposed:</strong> {new Date(action.proposed_at).toLocaleString()}</p>
            {action.approved_at && (
              <p><strong>Approved:</strong> {new Date(action.approved_at).toLocaleString()} by {action.approved_by}</p>
            )}
          </div>

          {action.status === "proposed" && (
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => handleApprove(action.id)}
                disabled={loading === action.id}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                {loading === action.id ? "Processing..." : "Approve"}
              </button>
              <button
                onClick={() => handleReject(action.id)}
                disabled={loading === action.id}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                Reject
              </button>
            </div>
          )}

          {action.status === "completed" && action.result && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded">
              <p className="text-sm font-semibold text-green-800">Execution Result:</p>
              <pre className="text-xs mt-1 text-green-900">{JSON.stringify(action.result, null, 2)}</pre>
            </div>
          )}

          {action.status === "failed" && action.error_message && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm font-semibold text-red-800">Error:</p>
              <p className="text-xs mt-1 text-red-900">{action.error_message}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    proposed: "bg-yellow-100 text-yellow-800",
    approved: "bg-blue-100 text-blue-800",
    executing: "bg-purple-100 text-purple-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
    rejected: "bg-gray-100 text-gray-800",
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors[status] || "bg-gray-100 text-gray-800"}`}>
      {status.toUpperCase()}
    </span>
  );
}
