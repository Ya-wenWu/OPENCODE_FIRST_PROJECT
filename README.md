# Agentic Workflow — 軟體開發自動化工具

一套基於 **ReAct (Reasoning + Acting)** 模式的自主 coding agent，串接 **NVIDIA NIM API**，能夠理解任務、呼叫工具、執行程式碼，自動完成軟體開發工作。

```
使用者的任務 → Agent 思考 → 呼叫工具 → 觀察結果 → 思考 → ... → 產出結果
```

---

## 快速開始

### 1. 環境需求

- Python 3.10+
- 一個 NVIDIA NIM API Key（免費，從 build.nvidia.com 取得）

### 2. 安裝

```bash
# 複製專案
git clone git@github.com:Ya-wenWu/OPENCODE_FIRST_PROJECT.git
cd OPENCODE_FIRST_PROJECT

# 建立虛擬環境並安裝依賴
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. 設定 API Key

```bash
export NVIDIA_API_KEY="nvapi-你的金鑰"
```

> 如何取得金鑰：到 [build.nvidia.com](https://build.nvidia.com) 註冊 → 頭像 → API Keys → Generate

### 4. 執行

```bash
.venv/bin/python -m agentic_workflow.cli "你的任務描述"
```

範例：

```bash
.venv/bin/python -m agentic_workflow.cli "寫一個 python 計算機腳本到 /tmp/calc.py"
```

---

## 架構說明

```
agentic_workflow/
├── cli.py                 ← 入口，處理命令列輸入
├── config.py              ← NVIDIA NIM 設定（model、API key）
├── core/
│   ├── schemas.py         ← 資料型別定義（Pydantic）
│   ├── llm.py             ← LLM 客戶端 + 自動重試
│   ├── tool_registry.py   ← 工具註冊中心
│   └── agent_loop.py      ← ReAct 主迴圈
└── tools/
    ├── bash.py            ← Shell 執行工具
    └── filesystem.py      ← 檔案讀寫工具
```

### 核心流程

```
                  ┌──────────────────────────┐
                  │     使用者輸入任務         │
                  └────────────┬─────────────┘
                               ↓
                  ┌──────────────────────────┐
                  │    Agent 決定下一步        │
                  │  (LLM 分析 + 選擇工具)     │
                  └────────────┬─────────────┘
                             ↙      ↘
                  ┌──────────┐    ┌──────────┐
                  │ 呼叫工具   │    │ 直接回答  │
                  │ (bash/讀寫)│    │ (任務完成)│
                  └────┬─────┘    └────┬─────┘
                       ↓               ↓
                  ┌──────────┐    ┌──────────┐
                  │ 觀察結果   │    │ 輸出結果   │
                  └──────────┘    └──────────┘
                       ↓
                  ┌──────────────────────────┐
                  │   回到「決定下一步」       │
                  │  (最多 10 次迭代)          │
                  └──────────────────────────┘
```

---

## 內建工具

| 工具 | 功能 | 範例 |
|------|------|------|
| `bash` | 執行 shell 命令 | `ls -la`, `python script.py` |
| `read` | 讀取檔案內容 | 閱讀原始碼、設定檔 |
| `write` | 寫入/建立檔案 | 產生程式碼、文件 |

---

## 設定選項

編輯 `agentic_workflow/config.py` 或設定環境變數：

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `NVIDIA_API_KEY` | — | API 金鑰（必要） |
| `MODEL` | `deepseek-ai/deepseek-v4-flash` | LLM 模型名稱 |
| `MAX_ITERATIONS` | `10` | 最大思考迭代次數 |
| `TEMPERATURE` | `0.1` | 模型隨機性（0=精確，1=創意） |

可用模型一覽（擇一設定）：

```
deepseek-ai/deepseek-v4-flash      # 快速編碼（預設）
nvidia/nemotron-3-super-120b-a12b  # 推理能力強
mistralai/mistral-small-4-119b-2603# 通用對話
qwen/qwen3.5-397b-a17b             # 高效能編碼
minimaxai/minimax-m2.7             # 辦公任務
```

---

## 貢獻

請見 [CONTRIBUTING.md](CONTRIBUTING.md) 與 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

## 安全性

### 專案層級

- **max_iterations=10** — 防止無限迴圈
- **Loop Detection** — 同一動作重複 3 次自動終止
- **30s 超時** — 每個 bash 指令最長 30 秒
- **Error handling** — API 失敗自動重試（最多 3 次）
- 所有工具在本地執行，不經第三方伺服器

### GitHub 層級

| 防護 | 狀態 |
|------|------|
| Secret scanning | ✅ 啟用 |
| Push protection | ✅ 啟用 |
| Dependabot alerts | ✅ 啟用 |
| Gitleaks (CI) | ✅ 每 PR 掃描 |
| Branch ruleset | ✅ 所有分支需 PR |
| AI Code Review | ✅ Gemini 審查 |

---

## 開發藍圖

- [x] Phase 1: ReAct Loop + 3 工具 + CLI
- [ ] Phase 2: 多 Agent 分工（Planner / Coder / Reviewer / Tester）
- [ ] Phase 3: 對話記憶持久化（JSONL / SQLite）
- [ ] Phase 4: Git 操作工具（commit / push / PR）
- [ ] Phase 5: 測試覆蓋 + 真實專案驗證

---

## 疑難排解

**Q: 出現 `NVIDIA_API_KEY not set`**
```bash
export NVIDIA_API_KEY="nvapi-你的金鑰"
```

**Q: 執行太久沒反應**
- 任務太複雜可調低 `MAX_ITERATIONS`
- 換較快模型如 `deepseek-ai/deepseek-v4-flash`

**Q: Rate limit 被擋**
- 免費方案每分鐘 40 次請求
- 等候 1 分鐘再試

---

## 技術棧

| 元件 | 技術 |
|------|------|
| LLM API | NVIDIA NIM (OpenAI 相容) |
| 型別驗證 | Pydantic v2 |
| HTTP 客戶端 | httpx |
| 重試機制 | tenacity |
| 設計模式 | ReAct Loop + Tool Registry |
