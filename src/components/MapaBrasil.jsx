import React, { useState, useEffect } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
} from "react-simple-maps";
import { scaleLinear } from "d3-scale";

const BRAZIL_TOPOJSON =
  "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson";

const estadosSiglaNome = {
  AC: "Acre",
  AL: "Alagoas",
  AP: "Amapá",
  AM: "Amazonas",
  BA: "Bahia",
  CE: "Ceará",
  DF: "Distrito Federal",
  ES: "Espírito Santo",
  GO: "Goiás",
  MA: "Maranhão",
  MT: "Mato Grosso",
  MS: "Mato Grosso do Sul",
  MG: "Minas Gerais",
  PA: "Pará",
  PB: "Paraíba",
  PR: "Paraná",
  PE: "Pernambuco",
  PI: "Piauí",
  RJ: "Rio de Janeiro",
  RN: "Rio Grande do Norte",
  RS: "Rio Grande do Sul",
  RO: "Rondônia",
  RR: "Roraima",
  SC: "Santa Catarina",
  SP: "São Paulo",
  SE: "Sergipe",
  TO: "Tocantins"
};


export default function MapaBrasil() {
  const [anoSelecionado, setAnoSelecionado] = useState(2023);
  const [matriculasData, setMatriculasData] = useState({});
  const [hoveredEstado, setHoveredEstado] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:5000/matriculas-por-estado?ano=${anoSelecionado}`)
      .then((res) => {
        if (!res.ok) throw new Error("Erro ao buscar dados da API");
        return res.json();
      })
      .then((data) => setMatriculasData(data))
      .catch((err) => {
        console.error(err);
        setMatriculasData({});
      });
  }, [anoSelecionado]);

  const dadosAno = matriculasData || {};
  const valores = Object.values(dadosAno);
  const maxMatriculas = valores.length > 0 ? Math.max(...valores) : 0;

  const colorScale = scaleLinear()
    .domain([0, maxMatriculas || 1])
    .range(["#ef9a9a", "#d32f2f"]);




  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: "30px",
        padding: "20px",
        backgroundColor: "#f0f0f0",
      }}
    >
      {/* Seletor de ano centralizado */}
      <div
        style={{
          textAlign: "center",
        }}
      >
        <label
          htmlFor="ano"
          style={{ fontSize: "18px", fontWeight: "bold", marginRight: "8px" }}
        >
          Selecione o ano:
        </label>
        <select
          id="ano"
          value={anoSelecionado}
          onChange={(e) => setAnoSelecionado(Number(e.target.value))}
          style={{
            fontSize: "16px",
            padding: "6px 10px",
            borderRadius: "4px",
          }}
        >
          <option value={2023}>2023</option>
          <option value={2024}>2024</option>
        </select>
      </div>

      {/* Container mapa + info */}
      <div
        style={{
          display: "flex",
          gap: "30px",
          alignItems: "flex-start",
          width: "700px", // largura fixa
          height: "700px", // altura fixa para não mudar ao passar o mouse
          backgroundColor: "#fff",
          padding: "20px",
          borderRadius: "8px",
          boxShadow: "0 0 10px rgba(0,0,0,0.1)",
        }}
      >
        {/* Mapa */}
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{ scale: 850, center: [-54, -15] }}
          width={700}
          height={700}
          style={{ flexShrink: 0 }}
        >
          <Geographies geography={BRAZIL_TOPOJSON}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const sigla =
                  geo.properties.sigla || geo.properties.UF || geo.id;

                const valor = dadosAno[sigla] || 0;

                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={colorScale(valor)}
                    stroke="#fff"
                    strokeWidth={0.5}
                    onMouseEnter={() => setHoveredEstado({ sigla, valor })}
                    onMouseLeave={() => setHoveredEstado(null)}
                    style={{
                      default: { outline: "none" },
                      hover: { outline: "none", cursor: "pointer", opacity: 0.8 },
                      pressed: { outline: "none" },
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ComposableMap>

        {/* Caixa info */}
        <div
          style={{
            width: "180px",
            height: "150px",
            border: "1px solid #ddd",
            borderRadius: "6px",
            padding: "15px",
            backgroundColor: "#fafafa",
            boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
            fontSize: "18px",
            fontWeight: "500",
            userSelect: "none",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            textAlign: "center",
            whiteSpace: "pre-line",
          }}
        >
          {hoveredEstado ? (
            <>
              <span style={{ fontWeight: "bold", fontSize: "22px" }}>
                {estadosSiglaNome[hoveredEstado.sigla] || hoveredEstado.sigla}
              </span>
              <span style={{ marginTop: "12px" }}>
                Matrículas: {hoveredEstado.valor.toLocaleString()}
              </span>
            </>
          ) : (
            "Passe o mouse\nsobre um estado"
          )}
        </div>
      </div>
    </div>
  );
}
