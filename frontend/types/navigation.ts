/**
 * Shared Navigation Type Definitions
 * Prevents tab type mismatches between components
 */

export type TabName = 'radio' | 'news' | 'music' | 'language' | 'apps' | 'settings';

export interface TabConfig {
  name: TabName;
  label: string;
  icon: string;
  activeIcon?: string;
  badge?: number;
}

export interface TabNavigatorProps {
  activeTab: TabName;
  onTabChange: (tab: TabName) => void;
  tabs?: TabConfig[];
  style?: any;
  showLabels?: boolean;
  orientation?: 'bottom' | 'top';
}

// Standard tab configuration - source of truth
export const STANDARD_TABS: TabConfig[] = [
  { 
    name: 'radio', 
    label: 'Radio', 
    icon: 'radio',
    activeIcon: 'radio',
  },
  { 
    name: 'news', 
    label: 'News', 
    icon: 'newspaper-outline',
    activeIcon: 'newspaper',
  },
  { 
    name: 'music', 
    label: 'Music', 
    icon: 'musical-notes-outline',
    activeIcon: 'musical-notes',
  },
  { 
    name: 'language', 
    label: 'Language', 
    icon: 'language-outline',
    activeIcon: 'language',
  },
  { 
    name: 'apps', 
    label: 'Apps', 
    icon: 'apps-outline',
    activeIcon: 'apps',
  },
  { 
    name: 'settings', 
    label: 'Settings', 
    icon: 'settings-outline',
    activeIcon: 'settings',
  },
];

// Type guard to validate tab names at runtime
export function isValidTabName(tab: string): tab is TabName {
  return ['radio', 'news', 'music', 'language', 'apps', 'settings'].includes(tab);
}

// Utility to get tab by name
export function getTabByName(name: TabName): TabConfig | undefined {
  return STANDARD_TABS.find(tab => tab.name === name);
}

// Performance monitoring type for tab switching
export interface TabSwitchMetrics {
  fromTab: TabName;
  toTab: TabName;
  switchTime: number;
  renderTime?: number;
  success: boolean;
}

// Tab rendering interface for main app
export interface TabRenderer {
  id: TabName;
  label: string;
  icon: string;
  render: () => React.ReactElement;
}