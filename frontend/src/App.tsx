import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import LandingPage from "./pages/LandingPage";
import AgentPage from "./pages/AgentPage";

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />

          <Route
            path="/marketing"
            element={
              <AgentPage
                agent="marketing"
                title="Marketing Advisor"
                icon="📊"
                accentColor="#3b82f6"
              />
            }
          />

          <Route
            path="/trader"
            element={
              <AgentPage
                agent="trader"
                title="SMC Trading Analyst"
                icon="📈"
                accentColor="#10b981"
              />
            }
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
