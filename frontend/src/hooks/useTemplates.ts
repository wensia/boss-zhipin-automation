/**
 * 问候模板管理 Hook
 */
import { useState, useCallback } from 'react';
import { get, post, patch, del } from '@/lib/api';
import type {
  GreetingTemplate,
  GreetingTemplateCreate,
  GreetingTemplateUpdate,
} from '@/types';

export function useTemplates() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getTemplates = useCallback(
    async (isActive?: boolean): Promise<GreetingTemplate[]> => {
      setLoading(true);
      setError(null);
      try {
        const endpoint =
          isActive !== undefined
            ? `/templates?is_active=${isActive}`
            : '/templates';
        return await get<GreetingTemplate[]>(endpoint);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to get templates';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getActiveTemplates = useCallback(async (): Promise<
    GreetingTemplate[]
  > => {
    setLoading(true);
    setError(null);
    try {
      return await get<GreetingTemplate[]>('/templates/active');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to get active templates';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getTemplate = useCallback(
    async (id: number): Promise<GreetingTemplate> => {
      setLoading(true);
      setError(null);
      try {
        return await get<GreetingTemplate>(`/templates/${id}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to get template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const createTemplate = useCallback(
    async (data: GreetingTemplateCreate): Promise<GreetingTemplate> => {
      setLoading(true);
      setError(null);
      try {
        return await post<GreetingTemplate>('/templates', data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to create template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateTemplate = useCallback(
    async (
      id: number,
      data: GreetingTemplateUpdate
    ): Promise<GreetingTemplate> => {
      setLoading(true);
      setError(null);
      try {
        return await patch<GreetingTemplate>(`/templates/${id}`, data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to update template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteTemplate = useCallback(
    async (id: number): Promise<{ message: string; template_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await del(`/templates/${id}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to delete template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const activateTemplate = useCallback(
    async (id: number): Promise<{ message: string; template_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post(`/templates/${id}/activate`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to activate template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deactivateTemplate = useCallback(
    async (id: number): Promise<{ message: string; template_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post(`/templates/${id}/deactivate`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to deactivate template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const duplicateTemplate = useCallback(
    async (id: number): Promise<GreetingTemplate> => {
      setLoading(true);
      setError(null);
      try {
        return await post<GreetingTemplate>(`/templates/${id}/duplicate`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to duplicate template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const previewTemplate = useCallback(
    async (params: {
      id: number;
      name: string;
      position: string;
      company?: string;
    }): Promise<{
      template_id: number;
      template_name: string;
      original_content: string;
      preview_content: string;
      variables_used: Record<string, string>;
    }> => {
      setLoading(true);
      setError(null);
      try {
        const queryParams = new URLSearchParams({
          name: params.name,
          position: params.position,
        });
        if (params.company) queryParams.set('company', params.company);

        return await get(`/templates/${params.id}/preview?${queryParams}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to preview template';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const batchDelete = useCallback(
    async (ids: number[]): Promise<{ message: string; deleted_count: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post('/templates/batch/delete', { template_ids: ids });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to delete templates';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    loading,
    error,
    getTemplates,
    getActiveTemplates,
    getTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    activateTemplate,
    deactivateTemplate,
    duplicateTemplate,
    previewTemplate,
    batchDelete,
  };
}
