import React, { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "./Sidebar";
import MapView from "./MapView";

const App = () => {
  const [cityNames, setCityNames] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<any | null>(null);
  const handleCitySelect = (cityName: string) => {setSelectedFeature(null); // we'll hook this up later
};

  useEffect(() => {
    axios.get("http://localhost:8000/")
      .then((res) => {
        setCityNames(res.data);
      });
  }, []);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: "0 0 250px", padding: "1rem", background: "#f4f4f4" }}>
        <Sidebar cityNames={cityNames} onSelect={handleCitySelect} />
      </div>
      <div style={{ flex: 1 }}>
        <MapView />
      </div>
    </div>
  );
};

export default App;


