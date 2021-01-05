<template>
  <v-container fluid>
    <v-row justify="end">
      <v-col cols="3">
        <v-select v-model="chart" :items="charts" label="Chart Type"></v-select>
      </v-col>
      <!-- <v-col cols="9">
        <v-select
          @input="updateSelectedUseClasses"
          :value="selectedUseClasses"
          :items="useClasses"
          multiple
          label="Use Class"
        ></v-select>
      </v-col> -->
      <v-col cols="3">
        <v-select
          @input="updateRange"
          :value="analysisRange"
          :items="ranges"
          label="Analysis Distance"
        ></v-select>
      </v-col>
      <v-col cols="3">
        <v-autocomplete
          v-on:input="updateStartYear"
          :value="startYear"
          :items="years"
          label="Start Year"
        ></v-autocomplete>
      </v-col>
      <v-col cols="3">
        <v-autocomplete
          v-on:input="updateEndYear"
          :value="endYear"
          :items="endYears"
          label="End Year"
        ></v-autocomplete>
      </v-col>
    </v-row>
    <v-row class="fill-height">
      <v-col cols="12">
        <div
          id="barplotparent"
          v-bind:style="parentStyle"
          v-if="chart == 'bar'"
        >
          <bar-plot
            :limitedData="limitedData"
            :yearRange="yearRange"
          ></bar-plot>
        </div>
        <div
          id="areaplotparent"
          v-bind:style="parentStyle"
          v-if="chart == 'area'"
        >
          <area-plot
            :limitedData="limitedData"
            :yearRange="yearRange"
          ></area-plot>
        </div>
        <div
          id="growthplotparent"
          v-bind:style="parentStyle"
          v-if="chart == 'growth'"
        >
          <growth-plot
            :limitedData="limitedGrowthData"
            :yearRange="yearRange"
          ></growth-plot>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue, { PropType } from "vue";
import { mapState } from "vuex";
import BarPlot from "@/components/barplot/BarPlot.vue";
import AreaPlot from "@/components/barplot/AreaPlot.vue";
import GrowthPlot from "@/components/barplot/GrowthPlot.vue";
import { HistDataItem, RootStateType, GrowthItem } from "@/store/state";
import _ from "lodash";

interface State {
  parentStyle: any;
  chart: string;
  charts: { text: string; value: string }[];
  ranges: { text: string; value: number }[];
}

export default Vue.extend({
  name: "BarPlotContainer",
  components: {
    BarPlot,
    AreaPlot,
    GrowthPlot,
  },
  data(): State {
    return {
      parentStyle: {
        width: "100%",
      },
      chart: "bar",
      charts: [
        { text: "Bar Chart", value: "bar" },
        { text: "Area Chart", value: "area" },
        { text: "Growth Chart", value: "growth" },
      ],
      ranges: [
        { text: "1 km", value: 1000 },
        { text: "5 km", value: 5000 },
        { text: "10 km", value: 10000 },
      ],
    };
  },
  props: {
    limitedData: {
      type: Array as PropType<HistDataItem[]>,
    },
    limitedGrowthData: {
      type: Array as PropType<GrowthItem[]>,
    },
  },
  mounted() {
    if (this.endYear > this.years[0]) {
      this.$store.dispatch("updateEndYear", this.years[0]);
    }
  },
  computed: {
    ...mapState({
      years: function (state: RootStateType) {
        const years = state.plotData.histData.map((el) => el.YEAR_BUILT);
        const sortYears = _.range(
          Math.min(...years),
          Math.max(...years) + 1
        ).reverse();
        return sortYears;
      },
      endYears: function (state: RootStateType) {
        const years = state.plotData.histData.map((el) => el.YEAR_BUILT);
        return _.range(Math.min(...years), Math.max(...years) + 1)
          .map((el) => ({
            value: el,
            text: el,
            disabled: el < state.plotControls.startYear,
          }))
          .reverse();
      },
      useClasses: (state: RootStateType) => state.plotData.useClasses,
      selectedUseClasses: (state: RootStateType) =>
        state.plotControls.selectedUseClasses,
      analysisRange: (state: RootStateType) => state.plotControls.analysisRange,
      startYear: (state: RootStateType) => state.plotControls.startYear,
      endYear: (state: RootStateType) => state.plotControls.endYear,
      yearRange: (state: RootStateType) => [
        state.plotControls.startYear,
        state.plotControls.endYear,
      ],
    }),
  },
  methods: {
    updateSelectedUseClasses(newValue: string[]) {
      this.$store.dispatch("updateSelectedUseClasses", newValue);
    },
    updateRange(newValue: number) {
      this.$store.dispatch("updateAnalysisRange", newValue);
    },
    updateStartYear(newValue: number) {
      this.$store.dispatch("updateStartYear", newValue);
    },
    updateEndYear(newValue: number) {
      this.$store.dispatch("updateEndYear", newValue);
    },
  },
});
</script>