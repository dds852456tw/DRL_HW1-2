# HW1-2: 策略顯示與價值評估 (Strategy Display and Value Evaluation) 實作紀錄

## 需求總覽
1. 顯示每個單元格的隨機生成行動（上下左右箭頭）作為策略 (Policy Matrix)。
2. 使用策略評估 (Policy Evaluation) 推導出每個狀態的價值 V(s) (Value Matrix)。
3. 以網頁應用程式顯示並允許互動操作障礙物/終點狀態。

## 開發過程
### 1. 專案建立與套件安裝
- 延續 Flask 開發基礎，建立新專案資料夾並初始化 Git。
- 安裝 NumPy 套件 (`pip install numpy`)，以方便在後端進行陣列與矩陣的數值計算。

### 2. 前端開發 (HTML/CSS/JavaScript)
- **介面配置**：
  - 設計並排的兩個區塊：左側為「價值矩陣 (Value Matrix)」，右側為「策略矩陣 (Policy Matrix)」。
  - 增設控制列：包含一個數字輸入欄 (維度 n)、初始化網格按鈕、產生隨機策略按鈕與評估策略按鈕。
- **網格狀態與顯示 (JavaScript)**：
  - 狀態管理：維護 `cellStates` 物件負責記錄每個座標是一般(normal)、障礙(obstacle)或終端(terminal)，對應顏色依序是白、灰、紅。利用點擊事件進行循環狀態切換。
  - 政策顯示：`cellPolicies` 記錄該單元格有哪些可選方向。
  - 對於隨機策略功能：針對一般狀態點，隨機配發一至多個可行方向 (上、下、左、右箭頭顯示)。

### 3. 後端策略評估 (Flask API)
- 建立 `/evaluate` 的 POST 路由來接收目前的網格設定 (size、障礙物座標、終端點座標) 及隨機政策。
- **價值函數計算 (Policy Evaluation)**：
  - 初始化 V = 原點全為零矩陣。
  - Discount Factor $\gamma = 0.9$，門檻值為 `1e-4`。
  - **狀態迭代法 (Value Iteration/Policy Evaluation)**：對每個狀態點，若有政策，則對可行的動作(機率均等為 $1/|A|$) 尋找預期未來值 $v\_sum = \sum \pi \cdot [r + \gamma V(S')]$。
  - 邊界及障礙判斷：如果碰到邊界及障礙，狀態停留且獎勵為 -1。如果抵達標的(終端)，給予 +10 的獎勵並維持該點值為設定不再更新。
  - 透過迭代更新狀態陣列直至誤差小於門檻值 (Convergence) 或達到最大迴圈數。

### 4. 前後端整合測試
- 前端取得 JSON 格式的新 Value Matrix `data.values` 後，更新並保留至小數點後 2 位的格式，顯示於 Value Matrix 中對應各個狀態格內。
- 測試完成，推上 GitHub。
