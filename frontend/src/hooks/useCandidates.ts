/**
 * 候选人管理 Hook
 */
import { useState, useCallback } from 'react';
import { get, post, patch, del } from '@/lib/api';
import type {
  Candidate,
  CandidateCreate,
  CandidateUpdate,
  CandidateStats,
  CandidateStatus,
  GreetingRecord,
} from '@/types';

export function useCandidates() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getCandidates = useCallback(
    async (params?: {
      status?: CandidateStatus;
      search?: string;
      limit?: number;
      offset?: number;
    }): Promise<Candidate[]> => {
      setLoading(true);
      setError(null);
      try {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.set('status', params.status);
        if (params?.search) queryParams.set('search', params.search);
        if (params?.limit) queryParams.set('limit', params.limit.toString());
        if (params?.offset) queryParams.set('offset', params.offset.toString());

        const query = queryParams.toString();
        const endpoint = query ? `/candidates?${query}` : '/candidates';

        return await get<Candidate[]>(endpoint);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to get candidates';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getCandidate = useCallback(async (id: number): Promise<Candidate> => {
    setLoading(true);
    setError(null);
    try {
      return await get<Candidate>(`/candidates/${id}`);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to get candidate';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getStats = useCallback(async (): Promise<CandidateStats> => {
    setLoading(true);
    setError(null);
    try {
      return await get<CandidateStats>('/candidates/stats');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to get stats';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createCandidate = useCallback(
    async (data: CandidateCreate): Promise<Candidate> => {
      setLoading(true);
      setError(null);
      try {
        return await post<Candidate>('/candidates', data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to create candidate';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const updateCandidate = useCallback(
    async (id: number, data: CandidateUpdate): Promise<Candidate> => {
      setLoading(true);
      setError(null);
      try {
        return await patch<Candidate>(`/candidates/${id}`, data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to update candidate';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteCandidate = useCallback(
    async (id: number): Promise<{ message: string; candidate_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await del(`/candidates/${id}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to delete candidate';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getGreetings = useCallback(
    async (id: number): Promise<GreetingRecord[]> => {
      setLoading(true);
      setError(null);
      try {
        return await get<GreetingRecord[]>(`/candidates/${id}/greetings`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to get greetings';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const archiveCandidate = useCallback(
    async (id: number): Promise<{ message: string; candidate_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post(`/candidates/${id}/archive`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to archive candidate';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const batchUpdateStatus = useCallback(
    async (
      ids: number[],
      status: CandidateStatus
    ): Promise<{ message: string; updated_count: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post('/candidates/batch/update-status', {
          candidate_ids: ids,
          status,
        });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to update status';
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
        return await post('/candidates/batch/delete', { candidate_ids: ids });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to delete candidates';
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
    getCandidates,
    getCandidate,
    getStats,
    createCandidate,
    updateCandidate,
    deleteCandidate,
    getGreetings,
    archiveCandidate,
    batchUpdateStatus,
    batchDelete,
  };
}
