/**
 * Extract the actual data payload from Backend's standardized response.
 * Backend always returns: { success: bool, message: string, data: any }
 */
export const extractData = (response) => {
  return response?.data?.data ?? response?.data;
};

/**
 * Extract error message from Backend error response.
 */
export const extractErrorMessage = (error) => {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    'An unexpected error occurred'
  );
};

/**
 * Standard error handler for API calls.
 * Maps HTTP status codes to user-friendly messages.
 */
export const handleApiError = (error, context = '') => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;
  const message = error?.response?.data?.message;

  switch (status) {
    case 400:
      return detail || message || 'Invalid request. Please check your input.';
    case 401:
      return 'Session expired. Please log in again.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return `${context || 'Resource'} not found.`;
    case 409:
      return detail || 'This record already exists.';
    case 422:
      return detail || 'Validation error. Please check your input.';
    case 500:
      return 'Server error. Please try again later.';
    default:
      if (!error?.response) {
        return 'Cannot connect to server. Please check if the backend is running.';
      }
      return detail || message || 'An unexpected error occurred.';
  }
};
