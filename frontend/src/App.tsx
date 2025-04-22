import React, { useEffect, useState } from "react";
import axios from "axios";
import Sidebar from "./Sidebar";
import MapView from "./MapView";

const BASE_URL = "http://localhost:8000";

const App = () => {
  const [cityNames, setCityNames] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<any | null>(null);
  const [placeTypes, setPlaceTypes] = useState<string[]>([]);
  const [selectedPlaceTypes, setSelectedPlaceTypes] = useState<string[]>([]);
  const [placeFeatures, setPlaceFeatures] = useState<any[]>([]);

  // Runs once on component mount, fetch all static data
  useEffect(() => {
    // Load city names with default (baltimore) selected
    axios.get(`${BASE_URL}`)
      .then((res) => {
        setCityNames(res.data);
        fetchFeature("Baltimore"); // Default load
      });

    // Load place_types
    axios.get(`${BASE_URL}/place_types/`)
    .then((res) => {
        setPlaceTypes(res.data)
    });
  }, []);

  const fetchFeature = (cityName: string) => {
    axios
        .get(`${BASE_URL}/locations/`, {
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

  const fetchPlaceFeatures = (types:string[], cityName:string) => {
    Promise.all(
        types.map((type) =>
            axios.get(`${BASE_URL}/places`, {
                params: {
                    place_type: type, 
                    location_name: cityName,
                },
            })
            .then((res) =>
                res.data.map((p:any) => ({
                    type:"Feature",
                    geometry: JSON.parse(p.geometry),
                    properties:{
                        name:p.name, 
                        desc: p.desc, 
                        place_type: type,
                    },
                }))
            )
        )
    ).then((results)=>{
        setPlaceFeatures(results.flat());
    });
  };

  const handleTogglePlaceType = (type:string, checked: boolean) =>{
    const updated=checked
    ? [...selectedPlaceTypes, type]
    : selectedPlaceTypes.filter((t)=> t!==type);

    setSelectedPlaceTypes(updated);
    if(selectedFeature) {
        fetchPlaceFeatures(updated, selectedFeature.properties.name)
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: "0 0 250px", padding: "1rem", background: "#f4f4f4" }}>
        <Sidebar cityNames={cityNames} placeTypes={placeTypes} onSelect={handleCitySelect} onTogglePlaceType={handleTogglePlaceType}/>
      </div>
      <div style={{ flex: 1 }}>
        <MapView selectedFeature={selectedFeature} placeFeatures={placeFeatures} />
      </div>
    </div>
  );
};

export default App;


