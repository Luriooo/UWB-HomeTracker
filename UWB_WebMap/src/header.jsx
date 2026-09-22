function Header({ page, onNavigate, onReload }) {
  const navItem = (id, label) => (
    <li key={id}>
      <a
        href="#"
        className={page === id ? "active" : ""}
        onClick={(e) => {
          e.preventDefault();
          onNavigate(id);
        }}
      >
        {label}
      </a>
    </li>
  );

  return (
    <header>
      <img src="/Icon_UWB.svg"height="90px"alt="UWB logo"/>
      <h2>UWB-HomeTracker</h2>
      <h4>Mobile Geoanwendungen UWB Simulator Sommersemester 2026</h4>
      <nav>
        <ul>
          {navItem("home", "Home")}
          {navItem("about", "About")}
          {navItem("faq", "FAQ")}
          <li>
            <a href="#" className="refresh-button" onClick={(e) => {
              e.preventDefault();
              onReload();
              }}
            >
             Refresh Map
            </a>
          </li>
        </ul>
      </nav>
    </header>
  );
}
export default Header;