import React, { useEffect, useRef, useState } from "react";
import { Layer, Map, MapInstance, Source } from "@vis.gl/react-maplibre";
import axios from "axios";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const BASE_URL = import.meta.env.VITE_BASE_URL;

type MapViewProps = {
  selectedFeature: any | null;
  placeFeatures: any[];
  edgesFeatures: any[] | [];
};

const MapView = ({
  selectedFeature,
  placeFeatures,
  edgesFeatures,
}: MapViewProps) => {
  console.log("Selected feature in MapView:", selectedFeature);
  console.log("Selected placeFeature in MapView:", placeFeatures);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);
  const [snappedPointFeature, setSnappedPointFeature] = useState< any | null>(null);
  const [nearestNodeFeature, setNearestNodeFeature] = useState<any | null>(null);
  const [computedEdges, setComputedEdges] = useState<any | null>(null);
  const [isochronePlaces, setIsochronePlaces] = useState<any | null>(null);
  const [isochronePolygon, setIsochronePolygon] = useState<any | null>(null);


  // When selected feature changes (Location polygon?)
  useEffect(() => {
    if (selectedFeature) {
      const g = selectedFeature.geometry;
      if (!g || !g.type || !g.coordinates) {
        console.error("Invalid geometry:", g);
      }
    }
  }, [selectedFeature]);

  // useEffect(() => {
  //   if (!mapRef) return;

  //   const m = new maplibregl.Marker({ draggable: true })
  //     .setLngLat([-76.6122, 39.2904])
  //     .addTo(mapRef);

  //   m.on("dragend", () => {
  //     const { lat, lng } = m.getLngLat();
  //     console.log("Dropped at:", lat, lng);
  //   });

  //   setMarker(m);

  //   return () => m.remove();
  // }, [mapRef]); //runs once after map mounts?

  return (
    <div style={{ width: "100%", height: "100%", backgroundColor: "#ccc" }}>
      <Map
        mapLib={maplibregl}
        onLoad={(e) => {
          mapRef.current = e.target;
          const m = new maplibregl.Marker({ draggable: true })
            .setLngLat([-76.6122, 39.2904])
            .addTo(e.target);

          m.on("dragend", () => {
            const { lat, lng } = m.getLngLat();
            console.log("Dropped at:", lat, lng);

            axios.post(`${BASE_URL}/isochrone-pt/`, { lat, lng })
            .then((res) => {
              console.log("Backend response:", res.data);
              setSnappedPointFeature(res.data.snapped_point);
              setNearestNodeFeature(res.data.nearest_node);
              setComputedEdges(res.data.edges);
              setIsochronePolygon(res.data.polygon);
              setIsochronePlaces(res.data.places);

            });
          });
          markerRef.current = m;

          // if (markerRef.current) {
          //   markerRef.current.remove();
          // }
        }}
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
              "fill-opacity": 0.1,
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
        <Source
          id="edges-source"
          type="geojson"
          data={{
            type: "FeatureCollection",
            features: edgesFeatures || [],
          }}
        >
          <Layer
            id="edges-layer"
            type="line"
            paint={{
              "line-color": "#888",
              "line-width": 1.5,
            }}
          />
        </Source>
        <Source
          id="places-source"
          type="geojson"
          data={{
            type: "FeatureCollection",
            features: placeFeatures || [],
          }}
        >
          <Layer
            id="places-layer"
            type="circle"
            paint={{
              "circle-radius": 6,
              "circle-color": "#007cbf",
              "circle-stroke-width": 1,
              "circle-stroke-color": "#fff",
            }}
          />
        </Source>
        {snappedPointFeature && (
          <Source
          id="snapped-point-source"
          type="geojson"
          data={{
            type: "FeatureCollection",
            features: [snappedPointFeature],
          }}
          >
            <Layer
              id="snapped-point-layer"
              type="circle"
              paint={{
                "circle-radius": 8,
                "circle-color": "#00cc44",
                "circle-stroke-width": 2,
                "circle-stroke-color": "#fff"
              }}
            />
          </Source>
        )
        }
        {nearestNodeFeature && (
          <Source
            id="nearest-node-source"
            type="geojson"
            data={{
              type: "FeatureCollection",
              features: [nearestNodeFeature],
            }}
          >
            <Layer
              id="nearest-node-layer"
              type="circle"
              paint={{
                "circle-radius": 5,
                "circle-color": "#ff9900",
                "circle-stroke-width": 1,
                "circle-stroke-color": "#000"
              }}
            />
          </Source>
        )}
        {computedEdges && (
          <Source
            id="computed-edges-source"
            type="geojson"
            data={computedEdges}
          >
            <Layer
              id="computed-edges-layer"
              type="line"
              paint={{
                "line-color": "#3399ff",
                "line-width": 2
              }}
            />
          </Source>
        )}
        {isochronePolygon && (
          <Source
            id="isochrone-polygon-source"
            type="geojson"
            data={isochronePolygon}
          >
            <Layer
              id="isochrone-polygon-layer"
              type="fill"
              paint={{
                "fill-color": "#66c2a5",
                "fill-opacity": 0.3
              }}
            />
          </Source>
        )}

        {isochronePlaces && (
          <Source
            id="isochrone-places-source"
            type="geojson"
            data={isochronePlaces}
          >
            <Layer
              id="isochrone-places-layer"
              type="circle"
              paint={{
                "circle-radius": 5,
                "circle-color": "#d95f02",
                "circle-stroke-width": 1,
                "circle-stroke-color": "#fff"
              }}
            />
          </Source>
        )}

      </Map>
    </div>
  );
};

export default MapView;
