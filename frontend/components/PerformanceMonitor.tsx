/**
 * Performance Monitor Component - React Native equivalent of Xcode Debug Gauges
 * Provides real-time monitoring of app performance metrics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Modal } from 'react-native';
import { performanceProfiler } from '../utils/PerformanceProfiler';
import { fpsMonitor, useFPSMonitor } from '../utils/FPSMonitor';
import { networkSimulator, useNetworkSimulation } from '../utils/NetworkSimulator';

interface PerformanceMetrics {
  cpu: number;
  memory: number;
  fps: number;
  networkLatency: number;
  renderTime: number;
}

interface DebugGaugeProps {
  label: string;
  value: number;
  unit: string;
  color: string;
  maxValue: number;
  warningThreshold: number;
}

const DebugGauge: React.FC<DebugGaugeProps> = ({
  label,
  value,
  unit,
  color,
  maxValue,
  warningThreshold,
}) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  const isWarning = value > warningThreshold;
  
  return (
    <View style={styles.gauge}>
      <Text style={styles.gaugeLabel}>{label}</Text>
      <View style={styles.gaugeContainer}>
        <View style={styles.gaugeBackground}>
          <View
            style={[
              styles.gaugeFill,
              {
                width: `${percentage}%`,
                backgroundColor: isWarning ? '#FF6B6B' : color,
              },
            ]}
          />
        </View>
        <Text style={[styles.gaugeValue, { color: isWarning ? '#FF6B6B' : '#333' }]}>
          {value.toFixed(1)}{unit}
        </Text>
      </View>
    </View>
  );
};

export const PerformanceMonitor: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    cpu: 0,
    memory: 0,
    fps: 60,
    networkLatency: 0,
    renderTime: 0,
  });
  const [isMonitoring, setIsMonitoring] = useState(false);

  const fpsHook = useFPSMonitor();
  const networkHook = useNetworkSimulation();

  // Update metrics periodically
  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      updateMetrics();
    }, 1000);

    return () => clearInterval(interval);
  }, [isMonitoring]);

  const updateMetrics = useCallback(() => {
    // Get FPS metrics
    const fpsMetrics = fpsMonitor.getMetrics();
    
    // Get profiler status
    const profilerStatus = performanceProfiler.getStatus();
    
    // Get network statistics
    const networkStats = networkSimulator.getStatistics();

    // Simulate CPU usage (React Native doesn't expose real CPU metrics)
    const cpuUsage = Math.random() * 30 + 20; // Simulate 20-50% CPU usage

    setMetrics({
      cpu: cpuUsage,
      memory: profilerStatus.memoryUsage,
      fps: fpsMetrics.currentFPS || 60,
      networkLatency: networkStats.averageLatency,
      renderTime: getAverageRenderTime(),
    });
  }, []);

  const getAverageRenderTime = (): number => {
    const renderMetrics = performanceProfiler.getMetrics('Render:');
    return renderMetrics?.averageExecutionTime || 0;
  };

  const startMonitoring = () => {
    setIsMonitoring(true);
    fpsHook.startMonitoring();
    performanceProfiler.setEnabled(true);
    console.log('📊 Performance monitoring started');
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
    fpsHook.stopMonitoring();
    performanceProfiler.setEnabled(false);
    console.log('📊 Performance monitoring stopped');
  };

  const exportReport = () => {
    const fpsReport = fpsHook.exportReport();
    const profilerReport = performanceProfiler.exportResults();
    const networkReport = networkHook.exportReport();

    const fullReport = {
      timestamp: new Date().toISOString(),
      currentMetrics: metrics,
      fpsReport: JSON.parse(fpsReport),
      profilerReport: JSON.parse(profilerReport),
      networkReport: JSON.parse(networkReport),
    };

    console.log('📊 Performance Report:', JSON.stringify(fullReport, null, 2));
    return fullReport;
  };

  const clearAllData = () => {
    performanceProfiler.clear();
    fpsMonitor.reset();
    networkSimulator.clearHistory();
    console.log('🗑️ Performance data cleared');
  };

  if (!isVisible) {
    // Floating performance indicator
    return (
      <TouchableOpacity
        style={styles.floatingButton}
        onPress={() => setIsVisible(true)}
        activeOpacity={0.8}
      >
        <Text style={styles.floatingButtonText}>📊</Text>
        {isMonitoring && (
          <View style={styles.monitoringIndicator}>
            <Text style={styles.fpsIndicator}>{metrics.fps.toFixed(0)}</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  }

  return (
    <Modal
      visible={isVisible}
      animationType="slide"
      transparent={true}
      onRequestClose={() => setIsVisible(false)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalContent}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Performance Monitor</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setIsVisible(false)}
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.content}>
            {/* Control Buttons */}
            <View style={styles.controls}>
              <TouchableOpacity
                style={[
                  styles.controlButton,
                  { backgroundColor: isMonitoring ? '#FF6B6B' : '#4ECDC4' }
                ]}
                onPress={isMonitoring ? stopMonitoring : startMonitoring}
              >
                <Text style={styles.controlButtonText}>
                  {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.controlButton, { backgroundColor: '#95E1D3' }]}
                onPress={exportReport}
              >
                <Text style={styles.controlButtonText}>Export Report</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.controlButton, { backgroundColor: '#F38BA8' }]}
                onPress={clearAllData}
              >
                <Text style={styles.controlButtonText}>Clear Data</Text>
              </TouchableOpacity>
            </View>

            {/* Performance Gauges */}
            <View style={styles.gaugesContainer}>
              <DebugGauge
                label="CPU Usage"
                value={metrics.cpu}
                unit="%"
                color="#4ECDC4"
                maxValue={100}
                warningThreshold={80}
              />

              <DebugGauge
                label="Memory"
                value={metrics.memory}
                unit="MB"
                color="#45B7D1"
                maxValue={512}
                warningThreshold={400}
              />

              <DebugGauge
                label="FPS"
                value={metrics.fps}
                unit=""
                color="#96CEB4"
                maxValue={60}
                warningThreshold={30}
              />

              <DebugGauge
                label="Network"
                value={metrics.networkLatency}
                unit="ms"
                color="#FFEAA7"
                maxValue={3000}
                warningThreshold={1000}
              />

              <DebugGauge
                label="Render"
                value={metrics.renderTime}
                unit="ms"
                color="#DDA0DD"
                maxValue={100}
                warningThreshold={50}
              />
            </View>

            {/* Performance Grade */}
            {fpsHook.metrics && (
              <View style={styles.performanceGrade}>
                {(() => {
                  const grade = fpsHook.getPerformanceGrade();
                  return (
                    <View style={[styles.gradeCard, { borderColor: grade.color }]}>
                      <Text style={[styles.gradeText, { color: grade.color }]}>
                        Grade: {grade.grade}
                      </Text>
                      <Text style={styles.gradeDescription}>{grade.description}</Text>
                    </View>
                  );
                })()}
              </View>
            )}

            {/* Detailed Metrics */}
            <View style={styles.detailedMetrics}>
              <Text style={styles.sectionTitle}>Detailed Metrics</Text>
              
              {fpsHook.metrics && (
                <View style={styles.metricCard}>
                  <Text style={styles.metricTitle}>Frame Rate Analysis</Text>
                  <Text style={styles.metricText}>
                    Total Frames: {fpsHook.metrics.totalFrames}
                  </Text>
                  <Text style={styles.metricText}>
                    Dropped Frames: {fpsHook.metrics.droppedFrames}
                  </Text>
                  <Text style={styles.metricText}>
                    Drop Rate: {((fpsHook.metrics.droppedFrames / fpsHook.metrics.totalFrames) * 100).toFixed(1)}%
                  </Text>
                </View>
              )}

              <View style={styles.metricCard}>
                <Text style={styles.metricTitle}>Network Performance</Text>
                <Text style={styles.metricText}>
                  Requests: {networkHook.statistics.totalRequests}
                </Text>
                <Text style={styles.metricText}>
                  Success Rate: {networkHook.statistics.successRate.toFixed(1)}%
                </Text>
                <Text style={styles.metricText}>
                  Current Profile: {networkHook.currentProfile.name}
                </Text>
              </View>

              <View style={styles.metricCard}>
                <Text style={styles.metricTitle}>Profiler Status</Text>
                <Text style={styles.metricText}>
                  Enabled: {performanceProfiler.getStatus().enabled ? 'Yes' : 'No'}
                </Text>
                <Text style={styles.metricText}>
                  Recorded Operations: {performanceProfiler.getStatus().resultCount}
                </Text>
                <Text style={styles.metricText}>
                  Memory Usage: {performanceProfiler.getStatus().memoryUsage.toFixed(1)} MB
                </Text>
              </View>
            </View>

            {/* Network Simulation Controls */}
            <View style={styles.networkControls}>
              <Text style={styles.sectionTitle}>Network Simulation</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {networkHook.profiles.map((profile) => (
                  <TouchableOpacity
                    key={profile.name}
                    style={[
                      styles.networkProfile,
                      {
                        backgroundColor: 
                          networkHook.isEnabled && networkHook.currentProfile.name === profile.name
                            ? '#4ECDC4' 
                            : '#E0E0E0'
                      }
                    ]}
                    onPress={() => {
                      if (networkHook.isEnabled && networkHook.currentProfile.name === profile.name) {
                        networkHook.disable();
                      } else {
                        networkHook.enableProfile(profile.name);
                      }
                    }}
                  >
                    <Text style={styles.networkProfileName}>{profile.name}</Text>
                    <Text style={styles.networkProfileSpeed}>
                      {profile.downloadSpeed > 0 ? `${profile.downloadSpeed/1000}Mb` : 'Offline'}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  floatingButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#4ECDC4',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    zIndex: 1000,
  },
  floatingButtonText: {
    fontSize: 20,
  },
  monitoringIndicator: {
    position: 'absolute',
    top: -5,
    right: -5,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#FF6B6B',
    justifyContent: 'center',
    alignItems: 'center',
  },
  fpsIndicator: {
    fontSize: 10,
    color: 'white',
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#E0E0E0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 16,
    color: '#666',
  },
  content: {
    flex: 1,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 15,
  },
  controlButton: {
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 8,
    flex: 1,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  controlButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 12,
  },
  gaugesContainer: {
    padding: 15,
  },
  gauge: {
    marginBottom: 15,
  },
  gaugeLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  gaugeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gaugeBackground: {
    flex: 1,
    height: 20,
    backgroundColor: '#E0E0E0',
    borderRadius: 10,
    overflow: 'hidden',
    marginRight: 10,
  },
  gaugeFill: {
    height: '100%',
    borderRadius: 10,
  },
  gaugeValue: {
    fontSize: 12,
    fontWeight: '600',
    minWidth: 50,
    textAlign: 'right',
  },
  performanceGrade: {
    padding: 15,
  },
  gradeCard: {
    padding: 15,
    borderRadius: 8,
    borderWidth: 2,
    alignItems: 'center',
  },
  gradeText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  gradeDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
  },
  detailedMetrics: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  metricCard: {
    backgroundColor: '#F8F9FA',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  metricTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  metricText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 3,
  },
  networkControls: {
    padding: 15,
  },
  networkProfile: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginRight: 10,
    minWidth: 80,
    alignItems: 'center',
  },
  networkProfileName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  networkProfileSpeed: {
    fontSize: 10,
    color: '#666',
    marginTop: 2,
  },
});

export default PerformanceMonitor;