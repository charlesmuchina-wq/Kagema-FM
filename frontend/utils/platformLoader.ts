/**
 * Platform Loader Utility
 * Conditionally loads components based on platform to avoid bundling native modules on web
 */
import { Platform } from 'react-native';

export const isWeb = Platform.OS === 'web';

/**
 * Dynamically import components based on platform
 * This prevents native modules from being bundled on web
 */
export async function loadPlatformComponent<T>(
  componentName: string
): Promise<{ default: T }> {
  if (isWeb) {
    // For web, return a placeholder component
    return {
      default: (() => null) as any as T,
    };
  }
  
  // For native platforms, this won't be called since we use .web.tsx files
  return {
    default: (() => null) as any as T,
  };
}
