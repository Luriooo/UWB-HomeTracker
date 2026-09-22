export default function About() {
  return (
    <main className="app-content">
      <div className="ha-card">
        <div className="ha-card-header">
          <span className="ha-card-title">Über dieses Projekt</span>
        </div>
        <p>
          Diese Web-Anwendung visualisiert die Indoor-Lokalisierung eines
          UWB-Tags (z.&nbsp;B. an einem Schlüssel oder Smartphone) innerhalb einer
          simulierten Wohnung. Vier UWB-Anker können über das Simulations-UI im Backend platziert werden. 
          Das Python-Backend simuliert Signallaufzeiten, erzeugt
          daraus TDoA-Messungen (Time Difference of Arrival) und schätzt per
          nichtlinearem Least-Squares-Verfahren die Tag-Position. Die Position wird 
          über eine FastAPI-Schnittstelle in die Webmap übertragen und auf dem Wohnungsgrundriss
          dargestellt. Der Wohnungsgrundriss ist eine OpenLayers Map mit einer Custom Projektion auf Pixelbasis.
          Der Kartenextent und der ImageLayer mit dem Grundriss werden ebenfalls über die API-Schnittstelle an die Webmap übertragen.
        </p>
        <p>
          Das Projekt entstand im Rahmen des Studiengangs Geoinformation
          (Bachelor) an der Berliner Hochschule für Technik (BHT) im Modul Mobile Geoanwendungen und dient
          dazu, ein UWB-basiertes Ortungssystem ohne reale Hardware
          nachzubilden und dessen Genauigkeit zu bewerten.
        </p>
        
      </div>
    </main>
  );
}
