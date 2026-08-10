import { useState, useEffect } from 'react';

/**
 * Custom hook to debounce any rapidly changing value (e.g. search input).
 * @param {*} value - The input value to debounce
 * @param {number} delay - Delay in milliseconds (default: 300ms)
 * @returns {*} debouncedValue
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;
