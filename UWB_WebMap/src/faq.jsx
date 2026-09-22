const faqItems = [
  {
    q: "Was ist UWB (Ultra-Wideband)?",
    a: "Ein Funkstandard, der durch sehr kurze Impulse präzise Laufzeitmessungen erlaubt und dadurch Positionsbestimmungen im Zentimeterbereich ermöglicht – deutlich genauer als klassisches WLAN- oder Bluetooth-Tracking.",
  },
  {
    q: "Wie wird die Position berechnet?",
    a: "Über Time Difference of Arrival (TDoA): Die Ankunftszeiten des Signals an den vier Ankern werden relativ zu einem Referenzanker verglichen. Aus den Laufzeitdifferenzen schätzt ein nichtlineares Least-Squares-Verfahren die wahrscheinlichste Tag-Position.",
  },
  {
    q: "Warum wird simuliert statt mit echten Ankern gearbeitet?",
    a: "Reale UWB-Hardware ist teuer, und es existiert keine ausgereifte Simulationsumgebung (vergleichbar zu ROS/Gazebo) für UWB. Deshalb wurde die Signalausbreitung inklusive realistischem Zeitmessrauschen selbst in Python nachgebildet.",
  },
  {
    q: "Wie genau ist die Simulation?",
    a: "Der Fehler zwischen simulierter und geschätzter Position wird in Pixel berechnet und regelmäßig aktualisiert.",
  },
  {
    q: "Welche Technologien kommen zum Einsatz?",
    a: "React und OpenLayers im Frontend (Custom-Pixelprojektion), FastAPI und Python im Backend, Styling angelehnt an Home Assistant.",
  },
  {
    q: "Kann das System auf echte UWB-Hardware umgestellt werden?",
    a: "Ja da die API-Schnittstelle  unabhängig von der Datenquelle ist, ließe sich die Simulation später durch reale Ankermessungen ersetzen, ohne das Frontend anzupassen.",
  },
];

export default function Faq() {
  return (
    <main className="app-content">
      <div className="ha-card">
        <div className="ha-card-header">
          <span className="ha-card-title">Häufige Fragen</span>
        </div>
        {faqItems.map((item, i) => (
          <div key={i} className="faq-item">
            <p className="faq-question">{item.q}</p>
            <p className="faq-answer">{item.a}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
