type SidebarProps = {
    // I think i want the sidebar to always have city names and it shold be those tihng sin the db with city in location_type ...
    cityNames: string[]; 
    onSelect: (name:string) => void;
};

const Sidebar = ({ cityNames, onSelect }: SidebarProps) => (
    <div style={{ padding: "1rem" }}>
      <h3>Select a city</h3>
      <ul>
        {cityNames.map((city) => (
          <li key={city}>
            <button onClick={() => onSelect(city)}>{city}</button>
          </li>
        ))}
      </ul>
    </div>
  );
  
  export default Sidebar;
