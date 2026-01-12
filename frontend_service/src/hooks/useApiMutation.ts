import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

interface UseApiMutationResult<TData, TVariables> {
  mutate: (variables: TVariables) => Promise<void>;
  data: TData | null;
  isLoading: boolean;
  error: string;
  reset: () => void;
}

interface UseApiMutationOptions<TData, TVariables> {
  mutationFn: (variables: TVariables) => Promise<TData>;
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: string, variables: TVariables) => void;
}

/**
 * Base Hook for mutation requests (POST, PUT, DELETE).
 * @param mutationFn - Function for mutation api request.
 * @param onSuccess - Function on success request.
 * @param onError - Function on error request.
 */
export function useApiMutation<TData = void, TVariables = void>({
                                                                  mutationFn,
                                                                  onSuccess,
                                                                  onError,
                                                                }: UseApiMutationOptions<TData, TVariables>): UseApiMutationResult<TData, TVariables> {
  const [state, setState] = useState<{
    data: TData | null;
    isLoading: boolean;
    error: string;
  }>({
    data: null,
    isLoading: false,
    error: '',
  });

  const mutate = useCallback(
    async (variables: TVariables) => {
      setState((prev) => ({ ...prev, isLoading: true, error: '' }));

      try {
        const result = await mutationFn(variables);
        setState({ data: result, isLoading: false, error: '' });
        onSuccess?.(result, variables);
      } catch (err) {
        const errorMessage = err instanceof AxiosError
          ? err.response?.data?.detail || err.message
          : 'Unknown error';

        setState((prev) => ({ ...prev, isLoading: false, error: errorMessage }));
        onError?.(errorMessage, variables);
      }
    },
    [mutationFn, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setState({ data: null, isLoading: false, error: '' });
  }, []);

  return { ...state, mutate, reset };
}
