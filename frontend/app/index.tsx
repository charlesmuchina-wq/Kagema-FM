import { useEffect } from 'react';
import { router } from 'expo-router';

export default function Index() {
  useEffect(() => {
    // Automatically redirect to welcome page
    router.replace('/welcome');
  }, []);

  // Return null since we're immediately redirecting
  return null;
}