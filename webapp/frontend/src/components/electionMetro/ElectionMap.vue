<template>
  <div id="map" style="width: 100%; height: 100%"></div>
</template>

<script lang="ts">
import Vue, { PropType } from "vue";
//https://github.com/teastman/Leaflet.pattern
import L, { LatLngTuple, TileLayer, LatLngBounds, Circle } from "leaflet";
//@ts-ignore
import geojsonvt from "geojson-vt";
// import { LMap, LTileLayer, LMarker, LCircle } from "vue2-leaflet";
import { mapGetters, mapState } from "vuex";
import * as d3 from "d3";
import {
  NumberValue,
  RGBColor,
  ScaleLinear,
  ScaleOrdinal,
  ScaleSequential,
} from "d3";
import { GeoProjection } from "d3-geo";
import { FeatureCollection } from "geojson";
import _ from "lodash";
import "leaflet.heat";
import "leaflet.vectorgrid";
import "leaflet.pattern";
import { RootStateType, FeatureItem } from "@/store/state";
import { PrecinctItem } from "@/store/modules/election";
const apiKey = process.env.VUE_APP_HERE_API_KEY as string;

type ColorGenerator =
  | ScaleSequential<string, d3.NumberValue>
  | ScaleOrdinal<string, string>
  | ScaleLinear<string, number>;
// leaflet.pattern doesn't have typescript support so use any in place
type PatternGenerator = (
  propValue: string
) => Record<string, any> | (() => null);

function colorIsSequential(color: unknown): color is ScaleSequential<"string"> {
  return color !== null;
}

interface Feature {
  type: string;
  properties: { name: string }[];
  geometry: {
    type: string;
    coordinates: LatLngTuple;
  };
}

interface Features {
  type: string;
  features: Feature[];
}

interface MapData {
  url: string;
  zoom: { start: number; end: number };
  center: LatLngTuple;
  bounds: LatLngBounds | null;
  map: any;
  svg: any;
  svgGroup: any;
  layers: any[];
  tileLayer: TileLayer | null;
  currentLayer: TileLayer | null;
  circleLayer: Circle | null;
}

type DataPoints = [number, number];

export default Vue.extend({
  name: "ElectionMap",
  mounted() {
    this.initMap();
    // this.initLayers();
    this.getPrecincts().then(() => {
      this.initLayers();
      this.updateClosestIDStyles([]);
    });
  },
  beforeDestroy() {
    this.map.off();
    this.map.remove();
  },
  created() {
    this.updateLayers = _.debounce(this.updateLayers, 500);
  },
  props: {
    selectedFeatures: {
      type: Array as PropType<FeatureItem[]>,
    },
    selectedLocations: {
      type: Array as PropType<[number, number, number][]>,
    },
  },
  data(): MapData {
    return {
      url: `https://2.base.maps.ls.hereapi.com/maptile/2.1/maptile/newest/normal.day/{z}/{x}/{y}/512/png8?apiKey=${apiKey}&ppi=320`,
      zoom: { start: 12, end: 12 },
      center: [44.98752, -93.248841],
      bounds: null,
      map: null,
      svg: null,
      svgGroup: null,
      layers: [],
      tileLayer: null,
      currentLayer: null,
      circleLayer: null,
    };
  },
  computed: {
    ...mapGetters("model", {
      features: "metroFeatures",
      closestIDs: "closestIDs",
    }),
  },
  watch: {
    selectedProperty: function (newValue) {
      if (this.map && newValue) {
        this.initLayers();
      } else if (this.currentLayer) {
        this.map.removeLayer(this.currentLayer);
      }
    },
    features: function () {
      this.initLayers();
    },
    closestIDs: function (newValues, oldValues) {
      this.updateClosestIDStyles(oldValues);
    },
    selectedYear: function () {
      if (this.currentLayer) {
        this.map.removeLayer(this.currentLayer);
      }

      this.getPrecincts().then(() => {
        this.initLayers();
      });
    },
  },
  methods: {
    async getPrecincts() {
      await this.$store.dispatch("election/updateMetroParcels");
      this.initLayers();
    },
    updateLayers() {
      this.initLayers();
    },
    initMap() {
      this.map = L.map("map", {
        center: this.center,
        zoom: this.zoom.start,
      });
      this.tileLayer = L.tileLayer(this.url, {
        maxZoom: 15,
        attribution:
          "Map Tiles &copy; " +
          new Date().getFullYear() +
          " " +
          '<a href="http://developer.here.com">HERE</a>',
      });
      this.tileLayer.addTo(this.map);
      const centerLatLng = new L.LatLng(
        this.center[0] as number,
        this.center[1] as number
      );
      const centerPoint = this.map.latLngToContainerPoint(centerLatLng);
      // const offset = this.map.getSize().x * 0.2;
      // centerPoint.x += offset;

      // Set center to latLng
      this.map.panTo(this.map.layerPointToLatLng(centerPoint));
      // Calculate the offset
      // Then move the map
      // this.map.panBy(new L.Point(-offset, 0), { animate: false });
      // this.initLayers();
    },
    colorFactory(): ColorGenerator {
      const selectedProperty = "2020-2016";
      const propertyVals = this.features.map(
        (el: { properties: Record<string, number | string> }) =>
          el.properties[selectedProperty]
      );
      const propertyType = this.features[0].properties[selectedProperty];
      if (propertyType === "string") {
        // Set color scheme for parcel map
        propertyVals.sort();
        const unique = [...new Set<string>(propertyVals)];

        const scale: ScaleOrdinal<string, string> = d3
          .scaleOrdinal(d3.schemeCategory10)
          .domain(unique);
        return scale;
      } else {
        propertyVals.sort(d3.ascending);
        const domain = d3.extent(propertyVals as number[]);
        if (domain) {
          return d3
            .scaleLinear<string, number>()
            .domain([domain[0], 0, domain[1]] as number[])
            .range(["red", "white", "blue"]);
        } else {
          throw new Error("domain not found");
        }
      }
    },
    initLayers() {
      const self = this;
      const selectedYear = 2020;

      //@ts-ignore

      const selectedColorProperty = "2020-2016";
      // Define popup for parcel map
      function popup(e: any) {
        let propVal = e.layer.properties[selectedColorProperty];
        if (!Number.isNaN(propVal)) {
          const scale = selectedColorProperty.includes("margin") ? 1000 : 100;
          propVal = Math.round(propVal * scale) / scale;
        }
        L.popup()
          .setContent(
            `<span>Year: ${selectedYear}</span><br>` +
              `<span>${selectedColorProperty}: ${propVal}</span>`
            // "<span></span>"
          )
          .setLatLng(e.latlng)
          .openOn(self.map);
      }

      // Remove current overlay layer if it exists already
      if (this.currentLayer) {
        this.map.removeLayer(this.currentLayer);
      }

      // Construct GEOJson FeatureCollection
      const geoJsonConstruct = {
        type: "FeatureCollection",
        features: this.features.filter(
          (el: PrecinctItem) => el.properties.year == selectedYear
        ),
      };
      const color = this.colorFactory();
      const closestIDs = this.closestIDs;
      //@ts-ignore no types for vectorGrid
      this.currentLayer = L.vectorGrid.slicer(geoJsonConstruct, {
        getFeatureId: function (f: any) {
          return f.properties.id;
        },
        vectorTileLayerStyles: {
          sliced: function (properties: Record<string, string | number>) {
            //@ts-ignore
            let parcelColor = null;
            if (selectedColorProperty !== null) {
              parcelColor = d3
                .color(
                  (color(
                    //@ts-ignore
                    properties[selectedColorProperty]
                  ) as unknown) as RGBColor
                )
                .formatHex();
            }
            return {
              //@ts-ignore
              fill: true,
              fillColor: parcelColor,
              fillOpacity: closestIDs.includes(properties.id) ? 1 : 0.1,
              color: "black",
              opacity: closestIDs.includes(properties.id) ? 1 : 0.1,
              weight: closestIDs.includes(properties.id) ? 1 : 0.1,
            };
          },
        },
        maxZoom: 15,
        // indexMaxZoom: 5, // max zoom in the initial tile index
        interactive: true,
        // getFeatureId: function(feature) {
        //     return feature.properties["cartodb_id"]
        // }
      });
      this.tileLayer?.setOpacity(0.7);
      this.currentLayer?.addTo(this.map);
      this.currentLayer?.on("click", popup);
    },
    updateClosestIDStyles(oldIDs: number[]) {
      this.initLayers();
      //@ts-ignore
      // this.closestIDs.forEach((el) => this.currentLayer?.setFeatureStyle(el, { fillOpacity: 1 }));
      // //@ts-ignore
      // oldIDs.forEach((el) => this.currentLayer?.resetFeatureStyle(el));
    },
  },
});
</script>
