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

const Sidebar = ({
  cityNames,
  placeTypes,
  walkMinutes,
  selectedisoPlaceTypes,
  onSelect,
  onTogglePlaceType,
  onSetWalkMinutes,
  onToggleIsoPlaceType,
}: SidebarProps) => (
  <div id="sidebar" style={{ padding: "1rem" }}>
    <h3>Select a city</h3>
    <select
      onChange={(e) => onSelect(e.target.value)}
      defaultValue="Baltimore"
      style={{ padding: "0.5rem", fontSize: "1rem" }}
    >
      {cityNames.map((city) => (
        <option key={city} value={city}>
          {city}
        </option>
      ))}
    </select>

    <h3>Places</h3>
    {placeTypes.map((type) => (
      <div key={`places-${type}`}>
        <label>
          <input
            type="checkbox"
            onChange={(e) => onTogglePlaceType(type, e.target.checked)}
          />
          {type}
        </label>
      </div>
    ))}

    <h3>Isochrone Settings</h3>
    <label>
      Walk time (minutes):
      <input
        type="number"
        min="1"
        max="180"
        value={walkMinutes}
        onChange={(e) => onSetWalkMinutes(Number(e.target.value))}
        style={{ marginLeft: "0.5rem", width: "4rem" }}
      />
    </label>

    <div style={{ marginTop: "0.5rem" }}>
      {placeTypes.map((type) => (
        <div key={`iso-${type}`}>
          <label>
            <input
              type="checkbox"
              onChange={(e) => onToggleIsoPlaceType(type, e.target.checked)}
              checked={selectedisoPlaceTypes.includes(type)}
            />
            {type}
          </label>
        </div>
      ))}
    </div>
  </div>
);

export default Sidebar;
