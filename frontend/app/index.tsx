import React, { useEffect } from 'react';
import { router } from 'expo-router';

export default function Index() {
  useEffect(() => {
    // Redirect to home immediately
    router.replace('/home');
  }, []);

  return null;
}
