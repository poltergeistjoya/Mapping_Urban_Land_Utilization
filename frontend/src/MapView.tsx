import { Map } from "@vis.gl/react-maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

const MapView = () => {
  return (
    <div style={{ width: "100%", height: "100%", backgroundColor: "#ccc" }}>
    <Map
      initialViewState={{
        longitude: -76.6122,
        latitude: 39.2904,
        zoom: 10,
      }}
      style={{ width: "100%", height: "100%" }}
      mapStyle="https://demotiles.maplibre.org/style.json"
    />
  </div>
  );
};

export default MapView;
