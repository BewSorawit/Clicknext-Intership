import React, { useState } from "react";
import Register from "./components/Register";
import Login from "./components/Login";
import UploadImage from "./components/UploadImage";

function App() {
  const [accessToken, setAccessToken] = useState(null);

  return (
    <div>
      <h1>Face Detection App</h1>
      {!accessToken ? (
        <div>
          <Register />
          <Login onLogin={setAccessToken} />
        </div>
      ) : (
        <UploadImage accessToken={accessToken} />
      )}
    </div>
  );
}

export default App;
