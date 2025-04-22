type SidebarProps = {
    cityNames: string[]; 
    placeTypes: string[];
    onSelect: (name:string) => void;
    onTogglePlaceType: (type:string, checked:boolean) => void;
};

const Sidebar = ({ cityNames, placeTypes, onSelect, onTogglePlaceType }: SidebarProps) => (
    <div id="sidebar" style={{ padding: "1rem" }}>
      <h3>Select a city</h3>
      <select
      onChange={(e)=> onSelect(e.target.value)}
      defaultValue="Baltimore"
      style={{padding: "0.5rem", fontSize: "1rem" }}
      >
        {cityNames.map((city) => (
            <option key={city} value={city}>
                {city}
            </option>
        ))}
      </select>

      <h3>Places</h3>
      {placeTypes.map((type)=>(
        <div key={type}>
            <label>
                <input type = "checkbox"
                onChange={(e) => onTogglePlaceType(type, e.target.checked)}/>
                {type}
            </label>
        </div>
      ))}
    </div>
  );
  
  export default Sidebar;
