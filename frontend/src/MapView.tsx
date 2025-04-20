import { Layer, Map, Source } from "@vis.gl/react-maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

type MapViewProps = {
  selectedFeature: any | null;
};

const MapView = ({ selectedFeature }: MapViewProps) => {
  return (
    <div style={{ width: "100%", height: "100%", backgroundColor: "#ccc" }}>
      <Map
        initialViewState={{
          longitude: -76.6122,
          latitude: 39.2904,
          zoom: 10,
        }}
        style={{ width: "100%", height: "100%" }}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
      >
        <Source
          id="polygon-source"
          type="geojson"
          data={{
            type: "FeatureCollection",
            features: selectedFeature ? [selectedFeature] : [],
          }}
        >
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
      </Map>
    </div>
  );
};

export default MapView;
