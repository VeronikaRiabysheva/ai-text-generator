import React, { useState } from "react";
import axios from "axios";
import { jsPDF } from "jspdf";
import "./index.css";

export default function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
   const [uploadMessage, setUploadMessage] = useState("");

const handleFileChange = (e) => {
  const selectedFiles = Array.from(e.target.files).filter(f => f.name.endsWith(".py"));

  if (selectedFiles.length !== e.target.files.length) {
    alert("Отфильтрованы файлы не-Python");
  }

  setFiles(selectedFiles);

  if (selectedFiles.length > 0) {
    // Если один файл
    if (selectedFiles.length === 1) {
      setUploadMessage(`Файл "${selectedFiles[0].name}" успешно загружен`);
    } else {
      // Несколько файлов
      const names = selectedFiles.map(f => f.name).join(", ");
      setUploadMessage(`Файлы (${selectedFiles.length}) успешно загружены: ${names}`);
    }
  } else {
    setUploadMessage(""); // если файлов нет
  }
};


  const handleSubmit = async () => {
    if (files.length === 0) return alert("Выберите хотя бы один Python файл");

    const formData = new FormData();
    files.forEach(f => formData.append("files", f));

    setLoading(true);
    setResults([]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/generate", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResults(res.data.results);
    } catch (err) {
      console.error(err);
      alert("Ошибка при генерации документации");
    } finally {
      setLoading(false);
    }
  };

  // ----------------- Скачивание PDF -----------------
  const downloadPDF = (filename, content) => {
    const doc = new jsPDF({
      orientation: "portrait",
      unit: "pt",
      format: "a4"
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 40;
    const text = content.split("\n");

    let y = 40;
    const lineHeight = 14;

    doc.setFont("Courier", "normal");
    doc.setFontSize(12);

    text.forEach((line) => {
      if (y > doc.internal.pageSize.getHeight() - 40) {
        doc.addPage();
        y = 40;
      }
      doc.text(line, margin, y);
      y += lineHeight;
    });

    doc.save(filename);
  };

  return (
    <>
   <div className="main-container">
        <div className="container">
            <h1>Автогенератор документации</h1>
                <div className="upload-warning">
                     <div className="waring-with-sign">
                         <div className="warning-img">
                              <img src="/img/warning-sign.webp"/></div>
                             <p>Наш генератор принимает только файлы с расширением .py. Пожалуйста, убедитесь, что загружаемые файлы соответствуют этому формату.</p>
                        </div>
                        <div className="waring-with-sign">
                        <div className="warning-img">
                        <img src="/img/red-sign.png"/></div>
                        <p>Генерация технической документации может занять несколько минут в зависимости от размера и сложности исходного кода. Пожалуйста, наберитесь терпения и не закрывайте страницу во время обработки.
                         </p>
                         </div>
                       </div>
                      <div className="upload-section">
                 <div className="upload-wrapper">
                  <input
                    id="fileInput"
                    type="file"
                    multiple
                    accept=".py"
                    style={{ display: "none" }}
                    onChange={handleFileChange}
                  />
              <button type="button" onClick={() => document.getElementById("fileInput").click()}>
                Выбрать файлы
              </button>
            </div>
            <button onClick={handleSubmit} disabled={loading || files.length === 0}>
              {loading ? "Генерация..." : "Сгенерировать файл"}
            </button>

          </div>
           {uploadMessage && <p className="upload-success">{uploadMessage}</p>}

          {results.length > 0 && (
            <div className="results">
              {results.map((res, idx) => (
                <div key={idx} className="file-block">
                  <h2>{res.file}</h2>
                  <div className="descriptions">
                    <div className="desc-block">
                      <h3>ИИ модель</h3>
                      <pre>{res.ai_description}</pre>
                      <button onClick={() => downloadPDF(`${res.file}_ai.pdf`, res.ai_description)}>Скачать ИИ PDF</button>
                    </div>
                    <div className="desc-block">
                     <div className="desc-block">
                      <h3>Чистый Python</h3>
                      <div className="python-desc">
                        {res.python_description.split("\n").map((line, idx) => {
                          // Выделяем ключевые метки жирным
                          if (line.startsWith("File:")) return <div key={idx}><strong>{line}</strong></div>;
                          if (line.startsWith("Classes:") || line.startsWith("Functions:") || line.startsWith("Dependencies:") || line.startsWith("Comments:"))
                            return <div key={idx}><strong>{line}</strong></div>;
                          if (line.startsWith(" - ")) return <div key={idx} style={{ marginLeft: 20 }}>{line}</div>; // методы/классы
                          if (line.startsWith("   ")) return <div key={idx} style={{ marginLeft: 40 }}>{line}</div>; // docstring, comments
                          return <div key={idx}>{line}</div>;
                        })}
                      </div>
                      <button onClick={() => downloadPDF(`${res.file}_python.pdf`, res.python_description)}>Скачать PDF</button>
                    </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
    </div>
   <div className="footer-container">
   <div className="footer">
    <p>Сделано с ❤️ в РФ :)</p>
    <p>© 2026 Veronika Riabysheva</p></div>
    </div>
 </>
);
}
