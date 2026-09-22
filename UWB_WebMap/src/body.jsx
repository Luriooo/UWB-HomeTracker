import { useEffect, useRef, useState } from "react";
import Map from "ol/Map";
import View from "ol/View";
import { defaults as defaultInteractions } from "ol/interaction";
import { defaults as controlDefaults } from "ol/control";
import ImageLayer from "ol/layer/Image";
import Static from "ol/source/ImageStatic";
import { Projection } from "ol/proj";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import { Style, Circle, Fill } from "ol/style";
import { getSignalPosition, getFloorplanData } from "./apihandling";

export default function Body({ refreshKey }) {
  const mapRef = useRef();
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
  let cleanupFn = () => {};
  let cancelled = false;

  const initializeMap = async () => {
    try {
        // Get floorplan information from API
        const floorplanData = await getFloorplanData();

        const extent = [
          0,
          0,
          floorplanData.Extent.x,
          floorplanData.Extent.y,
        ];

        // Projection Based on pixels and extend set to value from api
        const projection = new Projection({
          code: "floorplan",
          units: "pixels",
          extent,
        });

        // Floorplan image as Imagelayer
        const imageLayer = new ImageLayer({
          source: new Static({
            url: floorplanData.Floorplan_Path,
            projection,
            imageExtent: extent,
          }),
        });

        // Moving tag
        const tag = new Feature({
          geometry: new Point([]),
        });

        tag.setStyle(
          new Style({
            image: new Circle({
              radius: 6,
              fill: new Fill({ color: "red" }),
            }),
          })
        );

        // Anchors
        const anchors = [
          new Feature({
            geometry: new Point(floorplanData.Anchors[0]),
          }),
          new Feature({
            geometry: new Point(floorplanData.Anchors[1]),
          }),
          new Feature({
            geometry: new Point(floorplanData.Anchors[2]),
          }),
          new Feature({
            geometry: new Point(floorplanData.Anchors[3]),
          }),
        ];

        // Anchor style
        anchors.forEach((anchor) => {
          anchor.setStyle(
            new Style({
              image: new Circle({
                radius: 8,
                fill: new Fill({ color: "green" }),
              }),
            })
          );
        });

        // Vector layer
        const vectorLayer = new VectorLayer({
          source: new VectorSource({
            features: [tag, ...anchors],
          }),
        });

        // Map view
        const view = new View({
          projection,
          center: [
            floorplanData.Extent.x / 2,
            floorplanData.Extent.y / 2,
          ],
          enableRotation: false,
        });

        // Map
        const map = new Map({
          target: mapRef.current,
          layers: [
            imageLayer,
            vectorLayer,
          ],
          view,
          // default interactions blocked 
          interactions: defaultInteractions({
            mouseWheelZoom: false,
            doubleClickZoom: false,
            pinchZoom: false,
            dragZoom: false,
            dragPan: false,
          }),
          controls: controlDefaults({
            zoom: false,
            rotate: false,
          }),
        });

        // Fit map to floorplan
        map.getView().fit(extent, {
          size: map.getSize(),
        });

        // Map has successfully loaded
        setMapLoaded(true);

        // Signal API
        const updatePosition = async () => {
          try {
            const data = await getSignalPosition();

            tag.getGeometry().setCoordinates([
              data.estimated.x,
              data.estimated.y,
            ]);

            console.log(
              `True: (${data.true.x.toFixed(2)}, ${data.true.y.toFixed(2)})`
            );

            console.log(
              `Estimated: (${data.estimated.x.toFixed(2)}, ${data.estimated.y.toFixed(2)})`
            );

            console.log(
              `Error: ${data.error.toFixed(4)} px`
            );
          } catch (err) {
            console.error("Position update failed:", err);
          }
        };

        // Initial fetch
        updatePosition();

        // Update every 10 seconds
        const interval = setInterval(updatePosition, 5000);
       if (cancelled) {
        // Komponente/Effekt wurde schon wieder invalidiert, bevor der Fetch fertig war
        clearInterval(interval);
        map.setTarget(null);
        return;
      }

      cleanupFn = () => {
        clearInterval(interval);
        map.setTarget(null);
      };
    } catch (err) {
      console.error("Failed to initialize map:", err);
    }
  };

  initializeMap();

  return () => {
    cancelled = true;
    cleanupFn();
  };
}, [refreshKey]);

  return (
    <main className="app-content">
      <div className="ha-card">
        <div
          className="map-container"
          style={{
            position: "relative",
            width: "100%",
            height: "700px",
          }}>
          {!mapLoaded && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "white",
                zIndex: 10,
              }}
            >Loading map...
            </div>
          )}
          <div ref={mapRef}style={{width: "100%",height: "700px",}}/>
        </div>
      </div>
    </main>
  );
}