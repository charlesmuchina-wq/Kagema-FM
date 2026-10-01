/**
 * Shared radio Station type.
 *
 * Previously this interface was copy-defined in ~11 components/screens, which
 * caused "two different types with this name" TypeScript errors when a Station
 * from one module was passed to a component expecting another module's Station.
 * This single definition is the source of truth. `id` and `name` are the only
 * universally-required fields; everything else is optional so the type is a
 * superset compatible with every screen's usage.
 */
export interface Station {
  id: string;
  name: string;
  call_sign?: string;
  standard_display_name?: string;
  standardized_name?: string;
  stream_url?: string;
  country?: string;
  language?: string;
  genre?: string;
  latitude?: number;
  longitude?: number;
  quality_score?: number;
  division_level1?: string;
  division_level2?: string;
  added_at?: string;
  play_count?: number;
  last_played?: string;
}
