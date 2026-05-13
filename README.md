# 🎯 VisionSentinel

> Motor de visão computacional em tempo real — detecta, registra e analisa objetos em vídeo usando YOLOv8, SQLite e um dashboard interativo em Streamlit.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFAA?logo=yolo)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)
![CI](https://github.com/SEU_USUARIO/vision-sentinel/actions/workflows/ci.yml/badge.svg)

---

## ✨ O que este projeto faz

| Fase | Descrição |
|------|-----------|
| 📷 **Captura** | Webcam, arquivo de vídeo ou câmera IP (RTSP) |
| 🤖 **Inferência** | YOLOv8 detecta pessoas, carros, caminhões e bicicletas |
| 🗄️ **Persistência** | Cada detecção é gravada no SQLite com timestamp |
| 📊 **Dashboard** | KPIs, gráficos de linha, heatmap e tabela ao vivo |
| 🐳 **Deploy** | Dockerfile + Streamlit Cloud ready |

---

## 🖼️ Screenshots

> *Adicione um GIF gravado com [ScreenToGif](https://www.screentogif.com/) mostrando o sistema rodando.*

---

## 🛠️ Tecnologias

- **[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)** — modelo de detecção de objetos
- **OpenCV** — captura e anotação de frames
- **SQLite** — banco de dados leve, zero configuração
- **Streamlit + Plotly** — dashboard interativo
- **Python-dotenv** — gestão de configuração via `.env`
- **Docker** — empacotamento e portabilidade

---

## 🚀 Instalação e execução

### Pré-requisitos

- Python 3.11+
- Git
- (Opcional) Docker Desktop

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/vision-sentinel.git
cd vision-sentinel
```

### 2. Criar o ambiente virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar o ambiente

```bash
cp .env.example .env
# Edite o .env conforme necessário
```

### 5. Gerar dados de demonstração

```bash
python seed_data.py
```

### 6. Subir o dashboard

```bash
streamlit run dashboard/app.py
```

Acesse: **http://localhost:8501**

---

### 7. Rodar o motor de detecção (opcional)

```bash
# Webcam
python main.py --show

# Arquivo de vídeo
python main.py --source video.mp4 --show --save-video output.mp4

# Câmera IP (RTSP)
python main.py --source rtsp://usuario:senha@192.168.1.100:554/stream
```

---

## 🐳 Docker (execução em um comando)

```bash
# Gerar dados simulados primeiro
python seed_data.py

# Build e execução
docker compose up --build
```

Acesse: **http://localhost:8501**

---

## 📁 Estrutura do projeto

```
vision-sentinel/
├── main.py                  # Ponto de entrada do motor de detecção
├── seed_data.py             # Gerador de dados simulados
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example             # Template de variáveis de ambiente
├── .gitignore
│
├── src/
│   ├── detector.py          # Módulo de inferência YOLOv8
│   ├── database.py          # Camada de persistência SQLite
│   └── utils.py             # Logging, desenho de bounding boxes
│
├── dashboard/
│   └── app.py               # Interface Streamlit (BI Dashboard)
│
├── tests/
│   └── test_database.py     # Testes unitários
│
├── data/                    # Banco de dados (gerado em runtime, no .gitignore)
├── models/                  # Pesos YOLO (baixados automaticamente)
└── .github/
    └── workflows/
        └── ci.yml           # Pipeline de CI (GitHub Actions)
```

---

## ⚙️ Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MODEL_PATH` | `models/yolov8n.pt` | Caminho para o modelo YOLO |
| `CONFIDENCE_THRESHOLD` | `0.45` | Confiança mínima de detecção |
| `TARGET_CLASSES` | `person,car,truck,bicycle` | Classes monitoradas |
| `DB_PATH` | `data/detections.db` | Caminho do banco SQLite |

---

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 📜 Licença

MIT © 2024 — Seu Nome
