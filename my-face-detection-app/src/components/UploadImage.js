import React, { useState } from "react";
import axios from "axios";

function UploadImage({ accessToken }) {
  const [image, setImage] = useState(null);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!image) return;

    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Image = reader.result.split(",")[1];
      try {
        const response = await axios.post(
          "https://127.0.0.1:8000/face/detect_faces",
          {
            image_base64: base64Image,
          },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );
        const { result } = response.data;
        const link = document.createElement("a");
        link.href = `data:image/jpeg;base64,${result}`;
        link.download = "result.jpg";
        link.click();
      } catch (error) {
        console.error("Upload error:", error);
        alert("Upload failed");
      }
    };
    reader.readAsDataURL(image);
  };

  return (
    <div>
      <h2>Upload Image</h2>
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default UploadImage;
