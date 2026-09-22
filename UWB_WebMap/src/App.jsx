import { useState } from "react";
import Header from "./header";
import Body from "./body";
import About from "./about";
import Faq from "./faq";
import Footer from "./footer";
import "./App.css";

function App() {
  const [page, setPage] = useState("home");
  const [refreshKey, setRefreshKey] = useState(0);

  const handleReload = () => {
    console.log("Reload button clicked");
    setRefreshKey((prev) => prev + 1);
  };

  const renderPage = () => {
    switch (page) {
      case "about":
        return <About />;
      case "faq":
        return <Faq />;
      case "home":
      default:
        return <Body refreshKey={refreshKey} />;
    }
  };

  return (
    <div className="app">
      <Header
        page={page}
        onNavigate={setPage}
        onReload={handleReload}
      />
      {renderPage()}
      <Footer />
    </div>
  );
}
export default App;