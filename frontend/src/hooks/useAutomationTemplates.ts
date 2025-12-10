import { useState, useCallback } from 'react';
import type { AutomationTemplate, CreateTemplateData } from '@/types/template';

const API_BASE = '';

// Re-export types for convenience
export type { AutomationTemplate, CreateTemplateData };

export function useAutomationTemplates() {
  const [templates, setTemplates] = useState<AutomationTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async (accountId?: number) => {
    setLoading(true);
    setError(null);
    try {
      const url = accountId
        ? `${API_BASE}/api/automation-templates?account_id=${accountId}`
        : `${API_BASE}/api/automation-templates`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch templates');
      const data = await response.json();
      setTemplates(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch templates';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTemplate = useCallback(async (templateId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/automation-templates/${templateId}`);
      if (!response.ok) throw new Error('Failed to fetch template');
      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch template';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTemplate = useCallback(async (data: CreateTemplateData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/automation-templates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create template');
      }
      const newTemplate = await response.json();
      setTemplates(prev => [newTemplate, ...prev]);
      return newTemplate;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create template';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTemplate = useCallback(async (
    templateId: number,
    data: Partial<CreateTemplateData>
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/automation-templates/${templateId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to update template');
      const updatedTemplate = await response.json();
      setTemplates(prev => prev.map(t => (t.id === templateId ? updatedTemplate : t)));
      return updatedTemplate;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update template';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTemplate = useCallback(async (templateId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/automation-templates/${templateId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete template');
      setTemplates(prev => prev.filter(t => t.id !== templateId));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete template';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const useTemplate = useCallback(async (templateId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/automation-templates/${templateId}/use`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to update template usage');
      const updatedTemplate = await response.json();
      setTemplates(prev => prev.map(t => (t.id === templateId ? updatedTemplate : t)));
      return updatedTemplate;
    } catch (err) {
      console.error('Failed to update template usage:', err);
    }
  }, []);

  const duplicateTemplate = useCallback(async (templateId: number, newName?: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = newName
        ? `${API_BASE}/api/automation-templates/${templateId}/duplicate?new_name=${encodeURIComponent(newName)}`
        : `${API_BASE}/api/automation-templates/${templateId}/duplicate`;
      const response = await fetch(url, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to duplicate template');
      const newTemplate = await response.json();
      setTemplates(prev => [newTemplate, ...prev]);
      return newTemplate;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to duplicate template';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    templates,
    loading,
    error,
    fetchTemplates,
    fetchTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    useTemplate,
    duplicateTemplate,
  };
}
