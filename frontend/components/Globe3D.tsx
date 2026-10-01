import React, { useEffect, useRef, useState } from 'react';
import { Station } from '../types/station';
import { View, StyleSheet, Dimensions, ActivityIndicator, Text } from 'react-native';
// Web fallback - expo-gl and expo-three are not wired up here, so these are
// null stubs typed as `any`. The GL render path (onContextCreate) only runs when
// GLView is available; until expo-gl/expo-three are properly integrated this
// component renders its non-3D fallback. TODO: wire real 3D or remove dead path.
const GLView: any = null;
const Renderer: any = null;
const THREE: any = null;
import { Asset } from 'expo-asset';

const { width, height } = Dimensions.get('window');

interface Globe3DProps {
  stations: Station[];
  onStationPress?: (station: Station) => void;
  autoRotate?: boolean;
}

export const Globe3D: React.FC<Globe3DProps> = ({ 
  stations, 
  onStationPress, 
  autoRotate = true 
}) => {
  const [loading, setLoading] = useState(true);
  const globeRef = useRef<any>(null);
  // Initialize to null (not `new THREE.Group()`), which would throw at render
  // time because THREE is a null stub; the GL path lazily builds real objects.
  const stationMarkersRef = useRef<any>(null);

  const latLonToVector3 = (lat: number, lon: number, radius: number): any => {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);

    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const z = radius * Math.sin(phi) * Math.sin(theta);
    const y = radius * Math.cos(phi);

    return new THREE.Vector3(x, y, z);
  };

  const createStationMarker = (station: Station, radius: number): any => {
    const geometry = new THREE.SphereGeometry(0.05, 8, 8);
    const material = new THREE.MeshBasicMaterial({ 
      color: 0xFF6B35,
      transparent: true,
      opacity: 0.9
    });
    const marker = new THREE.Mesh(geometry, material);

    const position = latLonToVector3(station.latitude ?? 0, station.longitude ?? 0, radius + 0.05);
    marker.position.copy(position);

    // Add glow effect
    const glowGeometry = new THREE.SphereGeometry(0.08, 8, 8);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xFF6B35,
      transparent: true,
      opacity: 0.3
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    glow.position.copy(position);
    
    // Store station data
    (marker as any).userData = { station };

    return marker;
  };

  const onContextCreate = async (gl: any) => {
    try {
      // Setup renderer
      const renderer = new Renderer({ gl, alpha: true });
      renderer.setSize(gl.drawingBufferWidth, gl.drawingBufferHeight);
      renderer.setClearColor(0x000000, 0);

      // Setup scene
      const scene = new THREE.Scene();

      // Setup camera
      const camera = new THREE.PerspectiveCamera(
        45,
        gl.drawingBufferWidth / gl.drawingBufferHeight,
        0.1,
        1000
      );
      camera.position.z = 8;

      // Create Earth globe
      const globeRadius = 2;
      const globeGeometry = new THREE.SphereGeometry(globeRadius, 64, 64);
      
      // Create simple earth-like material
      const globeMaterial = new THREE.MeshPhongMaterial({
        color: 0x2233ff,
        emissive: 0x112244,
        shininess: 10,
        transparent: true,
        opacity: 0.9
      });

      const globe = new THREE.Mesh(globeGeometry, globeMaterial);
      globe.rotation.y = Math.PI;
      globeRef.current = globe;
      scene.add(globe);

      // Add atmosphere glow
      const atmosphereGeometry = new THREE.SphereGeometry(globeRadius + 0.1, 64, 64);
      const atmosphereMaterial = new THREE.MeshBasicMaterial({
        color: 0x4488ff,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide
      });
      const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
      scene.add(atmosphere);

      // Add station markers
      const markersGroup = stationMarkersRef.current;
      stations.forEach((station) => {
        if (station.latitude && station.longitude) {
          const marker = createStationMarker(station, globeRadius);
          markersGroup.add(marker);
          
          // Add glow
          const glowGeometry = new THREE.SphereGeometry(0.08, 8, 8);
          const glowMaterial = new THREE.MeshBasicMaterial({
            color: 0xFF6B35,
            transparent: true,
            opacity: 0.3
          });
          const glow = new THREE.Mesh(glowGeometry, glowMaterial);
          glow.position.copy(marker.position);
          markersGroup.add(glow);
        }
      });
      scene.add(markersGroup);

      // Add lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(5, 3, 5);
      scene.add(directionalLight);

      const backLight = new THREE.DirectionalLight(0x4488ff, 0.4);
      backLight.position.set(-5, -3, -5);
      scene.add(backLight);

      // Animation variables
      let frameId: number;
      let touchStartX = 0;
      let touchStartY = 0;
      let isDragging = false;
      let rotationSpeedX = 0;
      let rotationSpeedY = autoRotate ? 0.001 : 0;

      // Render loop
      const animate = () => {
        frameId = requestAnimationFrame(animate);

        // Auto-rotate or apply drag rotation
        if (globeRef.current) {
          globeRef.current.rotation.y += rotationSpeedY;
          globeRef.current.rotation.x += rotationSpeedX;
          
          // Damping
          if (!isDragging) {
            rotationSpeedX *= 0.95;
            if (!autoRotate) {
              rotationSpeedY *= 0.95;
            }
          }
        }

        // Rotate markers with globe
        if (markersGroup) {
          markersGroup.rotation.copy(globeRef.current?.rotation || new THREE.Euler());
        }

        renderer.render(scene, camera);
        gl.endFrameEXP();
      };

      animate();
      setLoading(false);

      // Cleanup
      return () => {
        cancelAnimationFrame(frameId);
        scene.clear();
        renderer.dispose();
      };
    } catch (error) {
      console.error('Error creating 3D globe:', error);
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FF6B35" />
          <Text style={styles.loadingText}>Loading Globe...</Text>
        </View>
      )}
      <GLView
        style={styles.glView}
        onContextCreate={onContextCreate}
      />
      <View style={styles.info}>
        <Text style={styles.infoText}>🌍 {stations.length} stations worldwide</Text>
        <Text style={styles.infoSubtext}>Swipe to rotate • Pinch to zoom</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  glView: {
    flex: 1,
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    zIndex: 10,
  },
  loadingText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginTop: 16,
    fontWeight: '600',
  },
  info: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(26, 31, 58, 0.95)',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 53, 0.5)',
  },
  infoText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 4,
  },
  infoSubtext: {
    color: '#8B92B0',
    fontSize: 12,
  },
});
