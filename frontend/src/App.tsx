import React, { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "./Sidebar";
import MapView from "./MapView";

const App = () => {
  const [cityNames, setCityNames] = useState<string[]>([]);
  const [features, setFeatures] = useState<any[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<any | null>(null);
// Load city names with default selected
  useEffect(() => {
    axios.get("http://localhost:8000/")
      .then((res) => {
        setCityNames(res.data);
        fetchFeature("Baltimore"); // Default load
      });
  }, []);

  const fetchFeature = (cityName: string) => {
    axios
        .get("http://localhost:8000/locations/", {
            params: {name: cityName },
        })
        .then((res) => {
            const features = res.data.map((loc: any) => ({
                type: "Feature",
                geometry: JSON.parse(loc.geometry),
                properties: { name: loc.name },
            }));

            setSelectedFeature(features[0]);
        });
  };

  const handleCitySelect = (cityName: string) => {
    fetchFeature(cityName);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: "0 0 250px", padding: "1rem", background: "#f4f4f4" }}>
        <Sidebar cityNames={cityNames} onSelect={handleCitySelect} />
      </div>
      <div style={{ flex: 1 }}>
        <MapView selectedFeature={selectedFeature} />
      </div>
    </div>
  );
};

export default App;


