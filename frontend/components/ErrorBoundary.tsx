import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { DESIGN_TOKENS } from '../constants/designTokens';
import { captureException } from '../utils/errorTracking';

interface Props {
  children: React.ReactNode;
  /** Optional custom fallback; receives the error and a reset callback. */
  fallback?: (error: Error, reset: () => void) => React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * App-level React error boundary. Catches render/lifecycle errors in the
 * subtree, reports them through the shared error tracker, and shows a
 * recoverable fallback instead of a white screen.
 */
export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    captureException(error, { componentStack: info.componentStack }, false);
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): React.ReactNode {
    const { hasError, error } = this.state;
    if (hasError && error) {
      if (this.props.fallback) {
        return this.props.fallback(error, this.handleReset);
      }
      return (
        <View style={styles.container}>
          <Text style={styles.emoji}>⚠️</Text>
          <Text style={styles.title}>Something went wrong</Text>
          <Text style={styles.message}>{error.message}</Text>
          <TouchableOpacity style={styles.button} onPress={this.handleReset}>
            <Text style={styles.buttonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      );
    }
    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: DESIGN_TOKENS.spacing.xl,
    backgroundColor: DESIGN_TOKENS.colors.background,
  },
  emoji: {
    fontSize: DESIGN_TOKENS.typography.size.hero,
    marginBottom: DESIGN_TOKENS.spacing.md,
  },
  title: {
    fontSize: DESIGN_TOKENS.typography.size.xxl,
    fontWeight: DESIGN_TOKENS.typography.weight.bold,
    color: DESIGN_TOKENS.colors.text.primary,
    marginBottom: DESIGN_TOKENS.spacing.sm,
    textAlign: 'center',
  },
  message: {
    fontSize: DESIGN_TOKENS.typography.size.md,
    color: DESIGN_TOKENS.colors.text.secondary,
    textAlign: 'center',
    marginBottom: DESIGN_TOKENS.spacing.xl,
  },
  button: {
    backgroundColor: DESIGN_TOKENS.colors.primary,
    paddingVertical: DESIGN_TOKENS.spacing.md,
    paddingHorizontal: DESIGN_TOKENS.spacing.xl,
    borderRadius: DESIGN_TOKENS.borderRadius.md,
  },
  buttonText: {
    color: DESIGN_TOKENS.colors.text.primary,
    fontSize: DESIGN_TOKENS.typography.size.lg,
    fontWeight: DESIGN_TOKENS.typography.weight.semibold,
  },
});
