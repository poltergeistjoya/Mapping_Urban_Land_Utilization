type SidebarProps = {
    // I think i want the sidebar to always have city names and it shold be those tihng sin the db with city in location_type ...
    cityNames: string[]; 
    onSelect: (name:string) => void;
};

const Sidebar = ({ cityNames, onSelect }: SidebarProps) => (
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
    </div>
  );
  
  export default Sidebar;
