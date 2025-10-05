import { useEffect, useRef, useState } from 'react';

interface MapSelectorProps {
  onLocationSelect: (lat: number, lng: number) => void;
  initialLat?: number;
  initialLng?: number;
  height?: string;
}

const MapSelector: React.FC<MapSelectorProps> = ({
  onLocationSelect,
  initialLat = 7.3000,
  initialLng = 5.1450,
  height = '400px'
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [marker, setMarker] = useState<any>(null);
  const [selectedLocation, setSelectedLocation] = useState({ lat: initialLat, lng: initialLng });

  useEffect(() => {
    if (typeof window !== 'undefined' && mapRef.current && !map) {
      const container = mapRef.current;
      
      // Dynamically import Leaflet
      import('leaflet').then((L) => {
        // Clear any existing map instance
        if (container._leaflet_id) {
          delete container._leaflet_id;
        }
        
        // Fix for default markers
        delete (L.Icon.Default.prototype as any)._getIconUrl;
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        });

        const mapInstance = L.map(container).setView([initialLat, initialLng], 15);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(mapInstance);

        const markerInstance = L.marker([initialLat, initialLng], { draggable: true }).addTo(mapInstance);

        markerInstance.on('dragend', (e: any) => {
          const position = e.target.getLatLng();
          setSelectedLocation({ lat: position.lat, lng: position.lng });
          onLocationSelect(position.lat, position.lng);
        });

        mapInstance.on('click', (e: any) => {
          const { lat, lng } = e.latlng;
          markerInstance.setLatLng([lat, lng]);
          setSelectedLocation({ lat, lng });
          onLocationSelect(lat, lng);
        });

        setMap(mapInstance);
        setMarker(markerInstance);
        
        // Fix map size after initialization
        setTimeout(() => {
          mapInstance.invalidateSize();
        }, 100);
      });
    }

    return () => {
      if (map) {
        try {
          map.remove();
        } catch (e) {
          // Ignore cleanup errors
        }
      }
      setMap(null);
      setMarker(null);
    };
  }, []);

  const presetLocations = [
    { name: 'FUTA Main Campus', lat: 7.3000, lng: 5.1450 },
    { name: 'FUTA Library', lat: 7.2995, lng: 5.1445 },
    { name: 'Engineering Building', lat: 7.3005, lng: 5.1455 },
  ];

  const selectPresetLocation = (lat: number, lng: number) => {
    if (map && marker) {
      map.setView([lat, lng], 15);
      marker.setLatLng([lat, lng]);
      setSelectedLocation({ lat, lng });
      onLocationSelect(lat, lng);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {presetLocations.map((location) => (
          <button
            key={location.name}
            onClick={() => selectPresetLocation(location.lat, location.lng)}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm hover:bg-blue-200 transition-colors"
          >
            📍 {location.name}
          </button>
        ))}
      </div>
      
      <div 
        ref={mapRef} 
        style={{ height, width: '100%' }}
        className="rounded-xl border-2 border-gray-200 overflow-hidden"
      />
      
      <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
        <p><strong>Selected:</strong> {selectedLocation.lat.toFixed(6)}, {selectedLocation.lng.toFixed(6)}</p>
        <p className="text-xs mt-1">💡 Click on the map or drag the marker to select a location</p>
      </div>
    </div>
  );
};

export default MapSelector;