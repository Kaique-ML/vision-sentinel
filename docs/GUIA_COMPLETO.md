# 📖 GUIA COMPLETO — VisionSentinel
### Do zero ao repositório no GitHub, instalação e deploy no Streamlit Cloud

---

## ÍNDICE

1. [Pré-requisitos — o que instalar antes de tudo](#1-pré-requisitos)
2. [Estrutura de pastas — o que foi criado e por quê](#2-estrutura-de-pastas)
3. [Configurar o Git localmente](#3-configurar-o-git-localmente)
4. [Criar o repositório no GitHub](#4-criar-o-repositório-no-github)
5. [Subir o projeto para o GitHub (primeiro push)](#5-subir-o-projeto-para-o-github)
6. [Instalar o projeto em sua máquina](#6-instalar-o-projeto-em-sua-máquina)
7. [Configurar variáveis de ambiente](#7-configurar-variáveis-de-ambiente)
8. [Gerar dados de demonstração](#8-gerar-dados-de-demonstração)
9. [Rodar o dashboard](#9-rodar-o-dashboard)
10. [Rodar o motor de detecção (câmera real)](#10-rodar-o-motor-de-detecção)
11. [Docker — rodar tudo com um comando](#11-docker)
12. [Deploy no Streamlit Cloud](#12-deploy-no-streamlit-cloud)
13. [GitHub Actions — CI automático](#13-github-actions)
14. [Fluxo de trabalho diário (git add, commit, push)](#14-fluxo-de-trabalho-diário)
15. [Perguntas frequentes e erros comuns](#15-erros-comuns)

---

## 1. Pré-requisitos

Antes de qualquer coisa, instale estas ferramentas na sua máquina.

### Python 3.11+

**Windows:**
1. Acesse https://www.python.org/downloads/
2. Baixe a versão 3.11 ou superior
3. Na instalação, MARQUE a opção **"Add Python to PATH"**
4. Clique em "Install Now"
5. Verifique: abra o terminal e digite:
   ```
   python --version
   ```
   Deve aparecer: `Python 3.11.x`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
python3.11 --version
```

**macOS:**
```bash
brew install python@3.11
python3 --version
```

---

### Git

**Windows:**
1. Acesse https://git-scm.com/download/win
2. Baixe e instale (pode deixar todas as opções padrão)
3. Verifique:
   ```
   git --version
   ```
   Deve aparecer: `git version 2.x.x`

**Linux:**
```bash
sudo apt install git -y
git --version
```

**macOS:**
```bash
brew install git
git --version
```

---

### Docker (opcional, mas recomendado)

1. Acesse https://www.docker.com/products/docker-desktop/
2. Baixe e instale o Docker Desktop para o seu sistema operacional
3. Abra o Docker Desktop e aguarde o ícone da baleia aparecer na barra de tarefas
4. Verifique:
   ```
   docker --version
   docker compose version
   ```

---

### Conta no GitHub

1. Acesse https://github.com
2. Clique em "Sign up"
3. Crie sua conta (é gratuita)
4. Confirme o e-mail

---

## 2. Estrutura de Pastas

Após configurar o projeto, sua estrutura ficará assim:

```
vision-sentinel/
│
├── main.py              ← Motor principal: captura vídeo + chama detector + grava no banco
├── seed_data.py         ← Gera dados falsos para testar o dashboard sem câmera
├── requirements.txt     ← Lista de bibliotecas Python que o projeto precisa
├── Dockerfile           ← Receita para empacotar o projeto em um container
├── docker-compose.yml   ← Orquestrador: sobe banco + dashboard com 1 comando
├── .env.example         ← Modelo de configuração (você copia e renomeia para .env)
├── .gitignore           ← Lista do que o Git deve IGNORAR (senhas, banco de dados, etc.)
├── README.md            ← Documentação pública do projeto (aparece no GitHub)
│
├── src/                 ← Código-fonte modular
│   ├── __init__.py
│   ├── detector.py      ← Carrega o YOLOv8 e faz a inferência nos frames
│   ├── database.py      ← Conecta ao SQLite e grava as detecções
│   └── utils.py         ← Funções auxiliares: logging, desenho de bounding boxes
│
├── dashboard/           ← Interface web (Streamlit)
│   ├── __init__.py
│   └── app.py           ← Dashboard com KPIs, gráficos e tabela
│
├── tests/               ← Testes automatizados
│   ├── __init__.py
│   └── test_database.py ← Testa se o banco de dados funciona corretamente
│
├── .streamlit/
│   └── config.toml      ← Configurações visuais do Streamlit (tema escuro, porta, etc.)
│
├── .github/
│   └── workflows/
│       └── ci.yml       ← Pipeline de CI: roda lint e testes a cada push
│
├── data/                ← CRIADA AUTOMATICAMENTE — guarda o banco .db (no .gitignore)
└── models/              ← CRIADA AUTOMATICAMENTE — guarda o modelo YOLO (no .gitignore)
```

**Por que modularizar assim?**
- `main.py` não sabe COMO detectar, ele só orquestra
- `detector.py` não sabe ONDE salvar, ele só detecta
- `database.py` não sabe NADA de vídeo, ele só persiste dados
- Isso torna cada arquivo testável, reutilizável e legível

---

## 3. Configurar o Git Localmente

Faça isso uma única vez na sua máquina.

```bash
git config --global user.name "Seu Nome Completo"
git config --global user.email "seu@email.com"
```

**Verifique se salvou:**
```bash
git config --global --list
```

Você deve ver:
```
user.name=Seu Nome Completo
user.email=seu@email.com
```

---

## 4. Criar o Repositório no GitHub

1. Acesse https://github.com e faça login
2. Clique no botão **"+"** no canto superior direito → **"New repository"**
3. Preencha:
   - **Repository name:** `vision-sentinel`
   - **Description:** `Motor de visão computacional com YOLOv8, SQLite e dashboard Streamlit`
   - **Visibility:** Public ✅ (para portfólio)
   - **NÃO** marque "Add a README file" (já temos um)
   - **NÃO** marque "Add .gitignore" (já temos um)
4. Clique em **"Create repository"**

O GitHub vai mostrar uma página com instruções. **Não feche essa aba ainda.**

---

## 5. Subir o Projeto para o GitHub (Primeiro Push)

Abra o terminal na pasta do projeto (`vision-sentinel/`) e execute os comandos um por um:

### 5.1 — Inicializar o repositório Git local

```bash
git init
```

Isso cria uma pasta oculta `.git` que rastreia todas as mudanças.

### 5.2 — Adicionar todos os arquivos ao "stage"

```bash
git add .
```

O ponto (`.`) significa "todos os arquivos". O `.gitignore` garante que `data/`, `models/`, `.env` e `venv/` NÃO sejam incluídos.

### 5.3 — Criar o primeiro commit

```bash
git commit -m "feat: estrutura inicial do VisionSentinel (MVP)"
```

Um commit é como um "checkpoint" — registra o estado atual do código com uma mensagem descritiva.

### 5.4 — Renomear a branch para "main"

```bash
git branch -M main
```

### 5.5 — Conectar ao repositório remoto

Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub:

```bash
git remote add origin https://github.com/SEU_USUARIO/vision-sentinel.git
```

### 5.6 — Enviar o código para o GitHub

```bash
git push -u origin main
```

Na primeira vez, o Git vai pedir suas credenciais do GitHub:
- **Username:** seu usuário do GitHub
- **Password:** NÃO use sua senha — use um **Personal Access Token**

**Como criar um Personal Access Token:**
1. GitHub → clique na foto do perfil → **Settings**
2. No menu lateral esquerdo, vá em **Developer settings** (lá embaixo)
3. Clique em **Personal access tokens** → **Tokens (classic)**
4. Clique em **Generate new token (classic)**
5. **Note:** `vision-sentinel-token`
6. **Expiration:** 90 days (ou sem expiração, como preferir)
7. Marque o escopo: **repo** (marque o checkbox principal)
8. Clique em **Generate token**
9. **COPIE O TOKEN AGORA** — ele não será mostrado novamente
10. Use esse token como "senha" quando o Git pedir

Após o push, acesse `https://github.com/SEU_USUARIO/vision-sentinel` e verá todos os arquivos lá.

---

## 6. Instalar o Projeto em Sua Máquina

(Se você clonar em outra máquina ou quiser reinstalar)

### 6.1 — Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/vision-sentinel.git
cd vision-sentinel
```

### 6.2 — Criar o ambiente virtual

O ambiente virtual isola as bibliotecas do projeto do resto do sistema.

```bash
python -m venv venv
```

### 6.3 — Ativar o ambiente virtual

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```
Se der erro de permissão:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Você saberá que funcionou quando o terminal mostrar `(venv)` no início.

### 6.4 — Instalar as dependências

```bash
pip install -r requirements.txt
```

Isso instalará: ultralytics (YOLOv8), opencv, streamlit, plotly, pandas, python-dotenv.

⚠️ O YOLOv8 é pesado (~500MB). A instalação pode demorar alguns minutos.

---

## 7. Configurar Variáveis de Ambiente

```bash
# Copie o template
cp .env.example .env
```

Abra o arquivo `.env` no seu editor e ajuste conforme necessário:

```env
MODEL_PATH=models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.45
TARGET_CLASSES=person,car,truck,bicycle
DB_PATH=data/detections.db
```

**Explicando cada variável:**

| Variável | O que faz |
|----------|-----------|
| `MODEL_PATH` | Onde o modelo YOLOv8 será salvo. O ultralytics baixa automaticamente se não existir. |
| `CONFIDENCE_THRESHOLD` | Detecções com confiança abaixo desse valor são descartadas. 0.45 = 45%. |
| `TARGET_CLASSES` | Somente essas classes serão gravadas no banco. Adicione `dog,cat` se quiser. |
| `DB_PATH` | Caminho do arquivo SQLite. A pasta `data/` é criada automaticamente. |

⚠️ **NUNCA suba o `.env` para o GitHub.** Ele já está no `.gitignore`, mas fique atento.

---

## 8. Gerar Dados de Demonstração

Para ver o dashboard funcionando sem precisar de câmera:

```bash
python seed_data.py
```

Isso cria `data/detections.db` com **5.000 detecções simuladas** dos últimos 30 dias,
com distribuição realista de horários (mais movimento de manhã e à tarde).

**Opções avançadas:**
```bash
# 7 dias de histórico com 2000 registros
python seed_data.py --days 7 --records 2000

# 60 dias com 15000 registros
python seed_data.py --days 60 --records 15000
```

---

## 9. Rodar o Dashboard

```bash
streamlit run dashboard/app.py
```

O terminal mostrará algo como:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Abra o navegador em **http://localhost:8501**

**Controles do dashboard:**
- **Período de análise:** quantos dias de histórico mostrar (1 a 30)
- **Classes:** filtrar por tipo de objeto detectado
- **Confiança mínima:** filtrar por nível de certeza
- **Atualizar dados:** força o recarregamento do banco (útil com motor rodando)

Para encerrar o Streamlit: pressione `Ctrl + C` no terminal.

---

## 10. Rodar o Motor de Detecção

Este módulo lê vídeo real, detecta objetos e grava no banco em tempo real.

### Webcam (câmera padrão do notebook)

```bash
python main.py --show
```

### Arquivo de vídeo local

```bash
python main.py --source /caminho/para/video.mp4 --show
```

### Salvar o vídeo processado

```bash
python main.py --source video.mp4 --show --save-video resultado.mp4
```

### Câmera IP (protocolo RTSP)

```bash
python main.py --source rtsp://admin:senha@192.168.1.100:554/stream --show
```

### Câmera IP sem exibição (modo servidor)

```bash
python main.py --source rtsp://admin:senha@192.168.1.100:554/stream
```

**Na primeira execução**, o YOLOv8 fará o download do modelo (~6MB para yolov8n).
Esse download acontece uma única vez.

Para encerrar: pressione `Q` na janela do vídeo, ou `Ctrl + C` no terminal.

---

## 11. Docker

O Docker permite rodar o projeto em qualquer máquina sem instalar Python ou dependências.

### 11.1 — Build da imagem

```bash
docker compose build
```

Isso lê o `Dockerfile`, instala tudo dentro de um container Linux.
Pode demorar 5–10 minutos na primeira vez.

### 11.2 — Subir o container

```bash
# Gere os dados simulados primeiro (fora do Docker)
python seed_data.py

# Sobe o container
docker compose up
```

Acesse: http://localhost:8501

### 11.3 — Rodar em background

```bash
docker compose up -d
```

### 11.4 — Ver logs

```bash
docker compose logs -f
```

### 11.5 — Parar

```bash
docker compose down
```

---

## 12. Deploy no Streamlit Cloud

O Streamlit Cloud hospeda seu dashboard gratuitamente com um link público.

### 12.1 — Preparar o banco para o deploy

O Streamlit Cloud não tem acesso ao seu banco local. Para o demo público, vamos commitar um banco pré-gerado.

**ATENÇÃO:** Por padrão, `data/` está no `.gitignore`. Para o deploy, faça uma exceção temporária:

```bash
# Gere o banco com dados de demo
python seed_data.py --days 30 --records 5000

# Force o git a rastrear este arquivo específico
git add -f data/detections.db
git commit -m "chore: adiciona banco de demo para deploy no Streamlit Cloud"
git push
```

Após o deploy, você pode remover o banco do git novamente se quiser.

### 12.2 — Criar conta no Streamlit Cloud

1. Acesse https://streamlit.io/cloud
2. Clique em **"Sign in"** → **"Continue with GitHub"**
3. Autorize o Streamlit a acessar seus repositórios

### 12.3 — Criar o app

1. Clique em **"New app"**
2. Preencha:
   - **Repository:** `SEU_USUARIO/vision-sentinel`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
3. Clique em **"Deploy!"**

O deploy demora 2–5 minutos. Ao finalizar, você receberá um link público como:
`https://seu-usuario-vision-sentinel-dashboardapp-xxxx.streamlit.app`

### 12.4 — Adicionar variáveis de ambiente no Streamlit Cloud

No Streamlit Cloud, clique em **"⚙️ Settings"** → **"Secrets"** e adicione:

```toml
DB_PATH = "data/detections.db"
MODEL_PATH = "models/yolov8n.pt"
CONFIDENCE_THRESHOLD = "0.45"
TARGET_CLASSES = "person,car,truck,bicycle"
```

---

## 13. GitHub Actions (CI automático)

O arquivo `.github/workflows/ci.yml` faz com que o GitHub rode lint e testes automaticamente a cada push.

**Como funciona:**
1. Você faz `git push`
2. O GitHub detecta o arquivo `.yml`
3. Cria uma máquina virtual Ubuntu temporária
4. Instala Python e as dependências
5. Roda o `flake8` (verifica estilo de código)
6. Roda o `pytest` (executa os testes)
7. Exibe ✅ ou ❌ no seu repositório

**Para ver o status:**
- No GitHub, clique na aba **"Actions"**
- Cada push terá um registro com o resultado

**O badge no README:**
```markdown
![CI](https://github.com/SEU_USUARIO/vision-sentinel/actions/workflows/ci.yml/badge.svg)
```
Substitua `SEU_USUARIO` pelo seu usuário real.

---

## 14. Fluxo de Trabalho Diário

Toda vez que você modificar o código e quiser salvar no GitHub:

### 14.1 — Ver o que mudou

```bash
git status
```

Mostra arquivos modificados (em vermelho) e prontos para commit (em verde).

### 14.2 — Adicionar as mudanças

```bash
# Adicionar um arquivo específico
git add src/detector.py

# Adicionar tudo de uma vez
git add .
```

### 14.3 — Criar o commit

```bash
git commit -m "feat: adiciona suporte a câmera RTSP"
```

**Convenção de mensagens de commit:**
| Prefixo | Quando usar |
|---------|-------------|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Atualização de documentação |
| `refactor:` | Melhoria de código sem mudar comportamento |
| `chore:` | Tarefas de manutenção (atualizar deps, etc.) |

### 14.4 — Enviar para o GitHub

```bash
git push
```

(Não precisa de `-u origin main` após o primeiro push)

---

## 15. Erros Comuns

### ❌ `ModuleNotFoundError: No module named 'ultralytics'`
**Causa:** Ambiente virtual não está ativado.
**Solução:**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

### ❌ `FileNotFoundError: data/detections.db`
**Causa:** Você não rodou o `seed_data.py` antes do dashboard.
**Solução:**
```bash
python seed_data.py
```

---

### ❌ `error: src refspec main does not match any`
**Causa:** Você não fez o primeiro `git commit` antes do `git push`.
**Solução:**
```bash
git add .
git commit -m "feat: commit inicial"
git push -u origin main
```

---

### ❌ `remote: Support for password authentication was removed`
**Causa:** GitHub parou de aceitar senhas normais. Use Personal Access Token.
**Solução:** Siga o passo 5.6 deste guia para criar um token.

---

### ❌ `Could not open VideoCapture` (câmera)
**Causa:** Número de câmera errado ou câmera em uso por outro programa.
**Solução:** Feche outros programas usando a câmera, ou tente `--source 1` em vez de `--source 0`.

---

### ❌ `streamlit: command not found`
**Causa:** Ambiente virtual não está ativado ou dependências não foram instaladas.
**Solução:**
```bash
source venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

---

### ❌ Docker: `permission denied while trying to connect to the Docker daemon`
**Causa:** Docker Desktop não está rodando.
**Solução:** Abra o Docker Desktop e aguarde o ícone da baleia ficar estável.

---

## 🎯 Checklist Final

Antes de compartilhar o link do projeto, verifique:

- [ ] O `.env` NÃO está no GitHub (verifique em `github.com/SEU_USUARIO/vision-sentinel`)
- [ ] O `README.md` tem a descrição, tecnologias e instruções de instalação
- [ ] O badge do CI está ✅ verde na aba Actions
- [ ] O link do Streamlit Cloud abre o dashboard sem erros
- [ ] O `README.md` tem o link do Streamlit Cloud

---

*Guia escrito para o projeto VisionSentinel — versão 1.0*
