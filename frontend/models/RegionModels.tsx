// Step 1: Define the data model
export interface Country {
  id: string;
  name: string;
  emoji: string;
  radioSource: string;
}

export interface Region {
  id: string;
  name: string;
  emoji: string;
  radioSource: string;
  countries: Country[];
}

export interface RegionsData {
  regions: Region[];
}

export interface LanguagesData {
  languages: Language[];
}

// Location detection result
export interface LocationInfo {
  country?: string;
  region?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
}

// Selection state for the picker
export interface Language {
  id: string;
  name: string;
  nativeName: string;
  code: string; // ISO 639-1 language code
  emoji: string;
  radioSources: string[]; // Multiple radio sources that support this language
}

export interface CountrySelection {
  selectedRegion: Region | null;
  selectedCountry: Country | null;
  selectedLanguage: Language | null;
  isWorldwide: boolean;
  isLanguageOnly: boolean; // New flag for language-only mode
}

// Props for the country picker component
export interface CountryPickerProps {
  onSelectionChange: (selection: CountrySelection) => void;
  initialSelection?: CountrySelection;
  autoDetectLocation?: boolean;
  style?: any;
}

// Helper type for picker display
export interface PickerOption {
  id: string;
  label: string;
  emoji: string;
  value: string;
}