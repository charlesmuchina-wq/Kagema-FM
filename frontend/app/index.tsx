import { Redirect } from 'expo-router';

export default function Index() {
  // Automatically redirect to welcome page
  return <Redirect href="/welcome" />;
}