import { ChangeEvent } from "react";

// Types
type SidebarProps = {
  cityNames: string[];
  placeTypes: string[];
  walkMinutes: number;
  selectedisoPlaceTypes: string[];
  onSelect: (name: string) => void;
  onTogglePlaceType: (type: string, checked: boolean) => void;
  onSetWalkMinutes: (minutes: number) => void;
  onToggleIsoPlaceType: (type: string, checked: boolean) => void;
};

// Styles
const styles = {
  sidebar: {
    padding: "1rem",
  },
  section: {
    marginBottom: "1.5rem",
  },
  heading: {
    fontSize: "1.1rem",
    fontWeight: 600,
    marginBottom: "0.75rem",
    color: "#333",
  },
  select: {
    padding: "0.5rem",
    fontSize: "1rem",
    width: "100%",
    borderRadius: "4px",
    border: "1px solid #ccc",
  },
  checkboxGroup: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "0.5rem",
  },
  checkboxLabel: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    fontSize: "0.9rem",
    cursor: "pointer",
  },
  numberInput: {
    marginLeft: "0.5rem",
    width: "4rem",
    padding: "0.25rem",
    borderRadius: "4px",
    border: "1px solid #ccc",
  },
};

const Sidebar = ({
  cityNames,
  placeTypes,
  walkMinutes,
  selectedisoPlaceTypes,
  onSelect,
  onTogglePlaceType,
  onSetWalkMinutes,
  onToggleIsoPlaceType,
}: SidebarProps) => {
  const handleCityChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onSelect(e.target.value);
  };

  const handleWalkMinutesChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (value >= 1 && value <= 180) {
      onSetWalkMinutes(value);
    }
  };

  return (
    <div style={styles.sidebar}>
      <div style={styles.section}>
        <h3 style={styles.heading}>Select a city</h3>
        <select
          onChange={handleCityChange}
          defaultValue="Baltimore"
          style={styles.select}
        >
          {cityNames.map((city) => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>
      </div>

      <div style={styles.section}>
        <h3 style={styles.heading}>Places</h3>
        <div style={styles.checkboxGroup}>
          {placeTypes.map((type) => (
            <label key={`places-${type}`} style={styles.checkboxLabel}>
              <input
                type="checkbox"
                onChange={(e) => onTogglePlaceType(type, e.target.checked)}
              />
              {type}
            </label>
          ))}
        </div>
      </div>

      <div style={styles.section}>
        <h3 style={styles.heading}>Isochrone Settings</h3>
        <label style={styles.checkboxLabel}>
          Walk time (minutes):
          <input
            type="number"
            min="1"
            max="180"
            value={walkMinutes}
            onChange={handleWalkMinutesChange}
            style={styles.numberInput}
          />
        </label>

        <div style={{ ...styles.checkboxGroup, marginTop: "0.75rem" }}>
          {placeTypes.map((type) => (
            <label key={`iso-${type}`} style={styles.checkboxLabel}>
              <input
                type="checkbox"
                onChange={(e) => onToggleIsoPlaceType(type, e.target.checked)}
                checked={selectedisoPlaceTypes.includes(type)}
              />
              {type}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
