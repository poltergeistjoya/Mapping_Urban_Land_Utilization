import React, { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "./Sidebar";
import MapView from "./MapView";
import LinearProgress from '@mui/material/LinearProgress';

const BASE_URL = import.meta.env.VITE_BASE_URL;

const App = () => {
  const [cityNames, setCityNames] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<any | null>(null);
  const [placeTypes, setPlaceTypes] = useState<string[]>([]);
  const [selectedPlaceTypes, setSelectedPlaceTypes] = useState<string[]>([]);
  const [placeFeatures, setPlaceFeatures] = useState<any[]>([]);
  const [edgesFeatures, setEdgesFeatures] = useState<any[]>([]);
  const [globalLoading, setGlobalLoading] = useState(false);
  const [walkMinutes, setWalkMinutes] = useState(15);
  const [selectedisoPlaceTypes, setSelectedisoPlaceTypes] = useState(["grocery_store"]);


  // Runs once on component mount, fetch all static data
  useEffect(() => {
    // Load city names with default (baltimore) selected
    axios.get(`${BASE_URL}`).then((res) => {
      setCityNames(res.data);
      fetchFeature("Baltimore"); // Default load
    });

    // Load place_types
    axios.get(`${BASE_URL}/place_types/`).then((res) => {
      setPlaceTypes(res.data);
    });
  }, []);

  useEffect(() => {
    // Global loading indicator logic
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

  const fetchFeature = (cityName: string) => {
    axios
      .get(`${BASE_URL}/locations/`, {
        params: { name: cityName },
      })
      .then((res) => {
        const features = res.data.map((loc: any) => ({
          type: "Feature",
          geometry: loc.geometry,
          properties: { name: loc.name },
        }));
        console.log("Raw API response:", res.data);
        console.log("Received location features:", features);
        console.log("First feature geometry:", features[0]?.geometry);

        setSelectedFeature(features[0]);
      });

    // //Get walk network
    // axios.get(`${BASE_URL}/edges/`, {
    //   params: {location_name:cityName },
    // }).then((res) => {
    //   setEdgesFeatures(res.data);
    // });
  };

  const handleCitySelect = (cityName: string) => {
    fetchFeature(cityName);
  };

  const fetchPlaceFeatures = (types: string[], cityName: string) => {
    Promise.all(
      types.map((type) =>
        axios
          .get(`${BASE_URL}/places`, {
            params: {
              place_type: type,
              location_name: cityName,
            },
          })
          .then((res) =>
            res.data.map((p: any) => ({
              type: "Feature",
              geometry: p.geometry,
              properties: {
                name: p.name,
                desc: p.desc,
                place_type: type,
              },
            })),
          ),
      ),
    ).then((results) => {
      setPlaceFeatures(results.flat());
    });
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

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div
        style={{ flex: "0 0 250px", padding: "1rem", background: "#f4f4f4" }}
      >
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
        />
      </div>
      <div style={{ flex: 1, position: "relative" }}>
      <MapView
        selectedFeature={selectedFeature}
        placeFeatures={placeFeatures}
        edgesFeatures={edgesFeatures}
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
