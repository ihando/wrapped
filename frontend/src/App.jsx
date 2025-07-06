import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function LoginPage() {
  const handleLogin = () => {
    window.location.href = "http://localhost:5001/login";
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        flexDirection: "column",
      }}
    >
      <h1>Spotify Wrapped</h1>
      <button
        onClick={handleLogin}
        style={{
          padding: "12px 24px",
          fontSize: "16px",
          backgroundColor: "#1db954",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Log in with Spotify
      </button>
    </div>
  );
}

function WrappedPage() {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/wrapped", {
      credentials: "include",
    })
      .then((res) => {
        if (res.status === 401) {
          window.location.href = "/";
          return;
        }
        return res.json();
      })
      .then((data) => {
        if (data && data.top_artists) {
          setArtists(data.top_artists);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching artists:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <p>Loading your wrapped...</p>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        flexDirection: "column",
      }}
    >
      <h1>Your Spotify Wrapped</h1>
      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
        {artists.map((artist) => (
          <button
            key={artist.name}
            style={{
              padding: "16px 24px",
              fontSize: "16px",
              backgroundColor: "#fff",
              color: "#000",
              border: "1px solid #ccc",
              borderRadius: "4px",
              cursor: "pointer",
              minWidth: "120px",
            }}
          >
            {artist.name}
          </button>
        ))}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/wrapped" element={<WrappedPage />} />
      </Routes>
    </Router>
  );
}

export default App;
