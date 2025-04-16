const express = require("express");
const { execFile } = require("child_process");
const cors = require("cors"); //  cors 모듈 추가
const app = express();
const port = 3000;

const allowedOrigins = ["https://easysub.kro.kr", "https://www.easysub.kro.kr"];
const corsOptions = {
  origin: function (origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true); // 허용된 origin
    } else {
      callback(new Error("Not allowed by CORS")); // 거절
    }
  },
  credentials: true,
};
app.use(cors(corsOptions)); // ✅ CORS 허용
app.use(express.json()); // ✅ JSON 요청 받기
app.options("/extract-subtitles", cors());

// 프론트에서 POST로 유튜브 링크 받아서 처리
app.post("/extract-subtitles", (req, res) => {
  const youtubeUrl = req.body.url;

  if (!youtubeUrl) {
    return res.status(400).json({ error: "YouTube URL is required" });
  }

  // 파이썬 스크립트 실행 (URL을 인자로 넘김)
  execFile(
    "python3",
    ["subtitle_extractor.py", youtubeUrl],
    (error, stdout, stderr) => {
      if (error) {
        console.error("Python error:", error);
        return res.status(500).json({ error: "Failed to extract subtitles" });
      }

      try {
        const jsonData = JSON.parse(stdout);
        res.json(jsonData); // 결과 JSON 그대로 프론트로 응답
      } catch (parseError) {
        console.error("JSON Parse Error:", parseError);
        res.status(500).json({ error: "Invalid JSON from Python" });
      }
    }
  );
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
