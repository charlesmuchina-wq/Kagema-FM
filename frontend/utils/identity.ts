/**
 * Device identity.
 *
 * Replaces the previous purely-local random userId with a server-backed anonymous
 * identity: on first launch the app registers once (POST /api/auth/anonymous),
 * then caches the returned userId + token in AsyncStorage and reuses them. If the
 * backend is unreachable, it falls back to a local id so the app still works
 * offline and upgrades to a server id on a later launch.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL =
  process.env.EXPO_PUBLIC_BACKEND_URL || 'https://radio-uifix.preview.emergentagent.com';

const USER_ID_KEY = 'user_id';
const TOKEN_KEY = 'auth_token';

export interface Identity {
  userId: string;
  token: string | null;
}

export async function getIdentity(): Promise<Identity> {
  let existingId: string | null = null;
  let existingToken: string | null = null;
  try {
    existingId = await AsyncStorage.getItem(USER_ID_KEY);
    existingToken = await AsyncStorage.getItem(TOKEN_KEY);
    // A server-issued identity is already cached.
    if (existingId && existingToken) {
      return { userId: existingId, token: existingToken };
    }

    const res = await fetch(`${API_BASE_URL}/api/auth/anonymous`, { method: 'POST' });
    const json = await res.json();
    if (json?.status === 'success' && json.data?.user_id) {
      await AsyncStorage.setItem(USER_ID_KEY, json.data.user_id);
      if (json.data.token) await AsyncStorage.setItem(TOKEN_KEY, json.data.token);
      return { userId: json.data.user_id, token: json.data.token ?? null };
    }
  } catch {
    // fall through to the offline fallback below
  }

  // Offline fallback: reuse any cached id, otherwise mint a local one.
  if (existingId) return { userId: existingId, token: existingToken };
  const localId = `local_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
  try {
    await AsyncStorage.setItem(USER_ID_KEY, localId);
  } catch {
    // ignore storage failure
  }
  return { userId: localId, token: null };
}

export async function getAuthToken(): Promise<string | null> {
  try {
    return await AsyncStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}
