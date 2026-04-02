const express = require("express");
const multer = require("multer");
const axios = require("axios");
const cors = require("cors");
const FormData = require("form-data");
const AdmZip = require("adm-zip");

const app = express();
app.use(cors());

const upload = multer({ storage: multer.memoryStorage() });

app.post("/upload", upload.array("resumes"), async (req, res) => {
  try {
    const formData = new FormData();
    formData.append("jd", req.body.jd);

    for (let file of req.files) {
      // 📦 If ZIP file
      if (file.originalname.endsWith(".zip")) {
        const zip = new AdmZip(file.buffer);
        const entries = zip.getEntries();

        entries.forEach(entry => {
          if (!entry.isDirectory) {
            const fileName = entry.entryName;

            // Only allow resumes
            if (
              fileName.endsWith(".pdf") ||
              fileName.endsWith(".docx")
            ) {
              formData.append(
                "resumes",
                entry.getData(),
                fileName
              );
            }
          }
        });
      } else {
        // Normal file
        formData.append("resumes", file.buffer, file.originalname);
      }
    }

    const response = await axios.post(
      "http://localhost:5001/analyze",
      formData,
      { headers: formData.getHeaders() }
    );

    res.json(response.data);

  } catch (err) {
    console.error(err);
    res.status(500).send("Error processing resumes");
  }
});

app.listen(5000, () => console.log("Backend running on port 5000"));