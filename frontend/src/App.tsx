import React, { useEffect, useState } from "react";
import { Map, Source, Layer } from "@vis.gl/react-maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import axios from "axios";

const API_URL = "http://localhost:8000/locations/"; // Backend API endpoint

const App = () => {
    const [geojsonData, setGeojsonData] = useState(null);

    useEffect(() => {
        console.log("use Effect is running ... fetching polygons");
        axios.get(API_URL)
            .then((response) => {
                console.log("Recieved data:", response.data);

                const features = response.data.map((location: any) => ({
                    type: "Feature",
                    geometry: JSON.parse(location.geometry),
                    properties: { name: location.name },
                }));

                setGeojsonData({
                    type: "FeatureCollection",
                    features,
                });
            })
            .catch((error) => console.error("Error fetching polygons:", error));
    }, []);

    return (
        <Map
            initialViewState={{
                longitude: -76.6122, // Center around Baltimore
                latitude: 39.2904,
                zoom: 10,
            }}
            style={{ width: "100vw", height: "100vh" }}
            mapStyle="https://demotiles.maplibre.org/style.json"
        >
            {geojsonData && (
                <Source id="polygon-source" type="geojson" data={geojsonData}>
                    <Layer
                        id="polygon-layer"
                        type="fill"
                        paint={{
                            "fill-color": "#ff0000",
                            "fill-opacity": 0.5,
                        }}
                    />
                    <Layer
                        id="polygon-border"
                        type="line"
                        paint={{
                            "line-color": "#000",
                            "line-width": 2,
                        }}
                    />
                </Source>
            )}
        </Map>
    );
};

export default App;
