import React, { useEffect, useRef, useState } from "react";
import {
  Layer,
  Map,
  Source,
  Popup
} from "@vis.gl/react-maplibre";
import axios from "axios";
import maplibregl, { MapGeoJSONFeature } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";


const BASE_URL = import.meta.env.VITE_BASE_URL;

type MapViewProps = {
  selectedFeature: any | null;
  placeFeatures: any[];
  edgesFeatures: any[];
};

const MapView = ({ selectedFeature, placeFeatures, edgesFeatures }: MapViewProps) => {
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);

  const [snappedPointFeature, setSnappedPointFeature] = useState<any | null>(null);
  const [nearestNodeFeature, setNearestNodeFeature] = useState<any | null>(null);
  const [computedEdges, setComputedEdges] = useState<any | null>(null);
  const [isochronePlaces, setIsochronePlaces] = useState<any | null>(null);
  const [isochronePolygon, setIsochronePolygon] = useState<any | null>(null);
  const [hoveredPlace, setHoveredPlace] = useState<MapGeoJSONFeature | null>(null);
  const [loadingIsochrone, setLoadingIsochrone] = useState(false);


  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const handleHover = (e: any) => {
      if (e.features?.length > 0) setHoveredPlace(e.features[0]);
      else setHoveredPlace(null);
    };

    map.on("mousemove", ["places-layer", "isochrone-places-layer"], handleHover);
    map.on("mouseleave", ["places-layer", "isochrone-places-layer"], () => setHoveredPlace(null));

    return () => {
      map.off("mousemove", handleHover);
      map.off("mouseleave", () => setHoveredPlace(null));
    };
  }, [mapRef.current]);

  return (
    <div style={{ width: "100%", height: "100%", backgroundColor: "#ccc" }}>
      <Map
        mapLib={maplibregl}
        onLoad={(e) => {
          const map = e.target;
          mapRef.current = map;

          const marker = new maplibregl.Marker({ draggable: true })
            .setLngLat([-76.6122, 39.2904])
            .addTo(map);

          marker.on("dragend", () => {
            const { lat, lng } = marker.getLngLat();
            setLoadingIsochrone(true);
            axios.post(`${BASE_URL}/isochrone-pt/`, { lat, lng })
              .then((res) => {
                setSnappedPointFeature(res.data.snapped_point);
                setNearestNodeFeature(res.data.nearest_node);
                setComputedEdges(res.data.edges);
                setIsochronePolygon(res.data.polygon);
                setIsochronePlaces(res.data.places);
              })
              .finally(() => setLoadingIsochrone(false));
          });

          markerRef.current = marker;
        }}
        initialViewState={{ longitude: -76.6122, latitude: 39.2904, zoom: 10 }}
        style={{ width: "100%", height: "100%" }}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
      >
        <Source id="polygon-source" type="geojson" data={{ type: "FeatureCollection", features: selectedFeature ? [selectedFeature] : [] }}>
          <Layer id="polygon-layer" type="fill" paint={{ "fill-color": "#ff0000", "fill-opacity": 0.1 }} />
          <Layer id="polygon-border" type="line" paint={{ "line-color": "#000", "line-width": 2 }} />
        </Source>

        <Source id="edges-source" type="geojson" data={{ type: "FeatureCollection", features: edgesFeatures || [] }}>
          <Layer id="edges-layer" type="line" paint={{ "line-color": "#888", "line-width": 1.5 }} />
        </Source>

        <Source id="places-source" type="geojson" data={{ type: "FeatureCollection", features: placeFeatures || [] }}>
          <Layer id="places-layer" type="circle" paint={{ "circle-radius": 6, "circle-color": "#007cbf", "circle-stroke-width": 1, "circle-stroke-color": "#fff" }} />
        </Source>

        {snappedPointFeature && (
          <Source id="snapped-point-source" type="geojson" data={{ type: "FeatureCollection", features: [snappedPointFeature] }}>
            <Layer id="snapped-point-layer" type="circle" paint={{ "circle-radius": 8, "circle-color": "#00cc44", "circle-stroke-width": 2, "circle-stroke-color": "#fff" }} />
          </Source>
        )}

        {nearestNodeFeature && (
          <Source id="nearest-node-source" type="geojson" data={{ type: "FeatureCollection", features: [nearestNodeFeature] }}>
            <Layer id="nearest-node-layer" type="circle" paint={{ "circle-radius": 5, "circle-color": "#ff9900", "circle-stroke-width": 1, "circle-stroke-color": "#000" }} />
          </Source>
        )}

        {computedEdges && (
          <Source id="computed-edges-source" type="geojson" data={computedEdges}>
            <Layer id="computed-edges-layer" type="line" paint={{ "line-color": "#3399ff", "line-width": 2 }} />
          </Source>
        )}

        {isochronePolygon && (
          <Source id="isochrone-polygon-source" type="geojson" data={isochronePolygon}>
            <Layer id="isochrone-polygon-layer" type="fill" paint={{ "fill-color": "#66c2a5", "fill-opacity": 0.3 }} />
          </Source>
        )}

        {isochronePlaces && (
          <Source id="isochrone-places-source" type="geojson" data={isochronePlaces}>
            <Layer id="isochrone-places-layer" type="circle" paint={{ "circle-radius": 5, "circle-color": "#d95f02", "circle-stroke-width": 1, "circle-stroke-color": "#fff" }} />
          </Source>
        )}

        {hoveredPlace && (
          <Popup
            longitude={hoveredPlace.geometry.coordinates[0]}
            latitude={hoveredPlace.geometry.coordinates[1]}
            anchor="top"
            closeButton={false}
            closeOnClick={false}
          >
            <div>
              <div style={{ fontSize: "14px", fontWeight: 700, textTransform: "uppercase", color: "#000" }}>
                {hoveredPlace.properties?.type || "(Unknown type)"}
              </div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "#000" }}>
                {hoveredPlace.properties?.name || "(Unnamed)"}
              </div>
              <div style={{ fontSize: "12px", color: "#000" }}>
                {hoveredPlace.properties?.desc || "(No description)"}
              </div>
            </div>
          </Popup>
        )}

      </Map>
    </div>
  );
};

export default MapView;
