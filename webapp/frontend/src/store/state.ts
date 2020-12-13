export type LocationDataItem = [number, number, number];

export interface HistDataItem {
  YEAR_BUILT: number;
  USECLASS1: string;
  COUNT: number;
}

export interface YearDataItem {
  YEAR_BUILT: number;
  COUNT: number;
}

export interface WeightDataItem {
  YEAR_BUILT: number;
  WEIGHT: number;
}

export interface HereAddress {
  title: string;
  id: string;
  resultType: string;
  houseNumberType: string;
  address: {
    label: string;
    countryCode: string;
    countryName: string;
    state: string;
    county: string;
    city: string;
    street: string;
    postalCode: string;
    houseNumber: string;
  };
  position: {
    lat: number | null;
    lng: number | null;
  };
  access: [
    {
      lat: number | null;
      lng: number | null;
    }
  ];
}

export interface PlotDataState {
  locationData: LocationDataItem[];
  histData: HistDataItem[];
  yearData: YearDataItem[];
  weightData: WeightDataItem[];
}

export interface RootStateType {
  address: string;
  addressInfo: HereAddress;
  plotData: PlotDataState;
  analysisDistance: number | null;
}

const rootState: RootStateType = {
  address: "",
  addressInfo: {
    title: "",
    id: "",
    resultType: "",
    houseNumberType: "",
    address: {
      label: "",
      countryCode: "",
      countryName: "",
      state: "",
      county: "",
      city: "",
      street: "",
      postalCode: "",
      houseNumber: "",
    },
    position: {
      lat: null,
      lng: null,
    },
    access: [
      {
        lat: null,
        lng: null,
      },
    ],
  },
  plotData: {
    locationData: [],
    histData: [],
    yearData: [],
    weightData: [],
  },
  analysisDistance: 5000,
};

export default rootState;
