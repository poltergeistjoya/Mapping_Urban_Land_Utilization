import { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "./Sidebar";
import MapView from "./MapView";
import LinearProgress from '@mui/material/LinearProgress';

// Use environment variable from Docker with fallback
const BASE_URL = import.meta.env.VITE_BASE_URL || "http://localhost:8000";
if (!import.meta.env.VITE_BASE_URL) {
  console.warn("VITE_BASE_URL not set, using default:", BASE_URL);
} else {
  console.log("Using BASE_URL from environment:", BASE_URL);
}

// Configure axios defaults
axios.defaults.withCredentials = true;  // Enable credentials
axios.defaults.headers.common['Accept'] = 'application/json';

// Add request interceptor for debugging
axios.interceptors.request.use(request => {
  console.log('Starting Request:', {
    url: request.url,
    method: request.method,
    headers: request.headers,
    baseURL: request.baseURL
  });
  return request;
});

// Add response interceptor for debugging
axios.interceptors.response.use(
  response => {
    console.log('Response:', {
      status: response.status,
      headers: response.headers,
      data: response.data
    });
    return response;
  },
  error => {
    console.error('Request Error:', {
      message: error.message,
      response: error.response ? {
        status: error.response.status,
        headers: error.response.headers,
        data: error.response.data
      } : 'No response',
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers,
        baseURL: error.config?.baseURL
      }
    });
    return Promise.reject(error);
  }
);

const DEFAULT_CITY = "Baltimore";

// Types
type Feature = {
  type: "Feature";
  geometry: {
    type: string;
    coordinates: number[];
  };
  properties: {
    name: string;
    [key: string]: any;
  };
};

type PlaceFeature = Feature & {
  properties: {
    name: string;
    desc: string;
    place_type: string;
  };
};

const App = () => {
  // State
  const [cityNames, setCityNames] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null);
  const [placeTypes, setPlaceTypes] = useState<string[]>([]);
  const [selectedPlaceTypes, setSelectedPlaceTypes] = useState<string[]>([]);
  const [placeFeatures, setPlaceFeatures] = useState<PlaceFeature[]>([]);
  const [globalLoading, setGlobalLoading] = useState(false);
  const [walkMinutes, setWalkMinutes] = useState(15);
  const [selectedisoPlaceTypes, setSelectedisoPlaceTypes] = useState<string[]>(["grocery_store"]);

  // API calls
  const fetchCityNames = async () => {
    try {
      const res = await axios.get<string[]>(`${BASE_URL}`);
      setCityNames(res.data);
      // Set Baltimore as default city
      if (res.data.includes(DEFAULT_CITY)) {
        fetchFeature(DEFAULT_CITY);
      }
    } catch (error) {
      console.error("Failed to fetch city names:", error);
    }
  };

  const fetchPlaceTypes = async () => {
    try {
      const res = await axios.get<string[]>(`${BASE_URL}/place_types/`);
      setPlaceTypes(res.data);
    } catch (error) {
      console.error("Failed to fetch place types:", error);
    }
  };

  const fetchFeature = async (cityName: string) => {
    try {
      const res = await axios.get(`${BASE_URL}/locations/`, {
        params: { name: cityName },
      });
      
      const features: Feature[] = res.data.map((loc: any) => ({
        type: "Feature",
        geometry: loc.geometry,
        properties: { name: loc.name },
      }));

      setSelectedFeature(features[0]);
    } catch (error) {
      console.error(`Failed to fetch feature for ${cityName}:`, error);
    }
  };

  const fetchPlaceFeatures = async (types: string[], cityName: string) => {
    try {
      const results = await Promise.all(
        types.map((type) =>
          axios.get(`${BASE_URL}/places`, {
            params: {
              place_type: type,
              location_name: cityName,
            },
          })
        )
      );

      const features: PlaceFeature[] = results.flatMap((res) =>
        res.data.map((p: any) => ({
          type: "Feature",
          geometry: p.geometry,
          properties: {
            name: p.name,
            desc: p.desc,
            place_type: p.place_type,
          },
        }))
      );

      setPlaceFeatures(features);
    } catch (error) {
      console.error("Failed to fetch place features:", error);
    }
  };

  // Event handlers
  const handleCitySelect = (cityName: string) => {
    fetchFeature(cityName);
  };

  const handleTogglePlaceType = (type: string, checked: boolean) => {
    const updated = checked
      ? [...selectedPlaceTypes, type]
      : selectedPlaceTypes.filter((t) => t !== type);

    setSelectedPlaceTypes(updated);
    if (selectedFeature) {
      fetchPlaceFeatures(updated, selectedFeature.properties.name);
    }
  };

  // Effects
  useEffect(() => {
    fetchCityNames();
    fetchPlaceTypes();
  }, []);

  useEffect(() => {
    const reqInterceptor = axios.interceptors.request.use((config) => {
      setGlobalLoading(true);
      return config;
    });
  
    const resInterceptor = axios.interceptors.response.use(
      (response) => {
        setGlobalLoading(false);
        return response;
      },
      (error) => {
        setGlobalLoading(false);
        return Promise.reject(error);
      }
    );
  
    return () => {
      axios.interceptors.request.eject(reqInterceptor);
      axios.interceptors.response.eject(resInterceptor);
    };
  }, []);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: "0 0 250px", padding: "1rem", background: "#f4f4f4" }}>
        <Sidebar
          cityNames={cityNames}
          placeTypes={placeTypes}
          onSelect={handleCitySelect}
          walkMinutes={walkMinutes}
          selectedisoPlaceTypes={selectedisoPlaceTypes}
          onSetWalkMinutes={setWalkMinutes}
          onToggleIsoPlaceType={(type, checked) =>
            setSelectedisoPlaceTypes((prev) =>
              checked ? [...prev, type] : prev.filter((t) => t !== type)
            )
          }
          onTogglePlaceType={handleTogglePlaceType}
        />
      </div>
      <div style={{ flex: 1, position: "relative" }}>
        <MapView
          selectedFeature={selectedFeature}
          placeFeatures={placeFeatures}
          edgesFeatures={[]}
          walkMinutes={walkMinutes}
          isoPlaceTypes={selectedisoPlaceTypes}
        />
        {globalLoading && (
          <div style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "4px",
            zIndex: 1000
          }}>
            <LinearProgress color="secondary" />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
