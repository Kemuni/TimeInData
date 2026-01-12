import {useEffect, useState, useCallback, useRef} from 'react';
import { AxiosError } from 'axios';

interface UseApiQueryResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string;
  refetch: () => Promise<void>;
}

interface UseApiQueryOptions<T> {
  queryFn: () => Promise<T>;
  enabled?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
}

/**
 * Base Hook for query api requests (GET).
 * @param queryFn - Function for api query request.
 * @param enabled - Boolean expression for enabling query request.
 * @param onSuccess - Function on success request.
 * @param onError - Function on error request.
 */
export function useApiQuery<T>(
  {
    queryFn,
    enabled = true,
    onSuccess,
    onError,
  }: UseApiQueryOptions<T>
): UseApiQueryResult<T> {
  const [state, setState] = useState<{
    data: T | null;
    isLoading: boolean;
    error: string;
  }>({
    data: null,
    isLoading: false,
    error: '',
  });

  const queryFnRef = useRef(queryFn);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    queryFnRef.current = queryFn;
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: '' }));

    try {
      const result = await queryFnRef.current();
      setState({ data: result, isLoading: false, error: '' });
      onSuccessRef.current?.(result);
    } catch (err) {
      let errorMessage: string;
      if (err instanceof AxiosError)
        errorMessage = err.response?.data?.detail || err.message;
      else
        throw err;

      setState({ data: null, isLoading: false, error: errorMessage });
      onErrorRef.current?.(errorMessage);
    }
  }, []);

  useEffect(() => {
    if (enabled) {
      fetchData();
    }
  }, [enabled, fetchData]);

  return { ...state, refetch: fetchData };
}
