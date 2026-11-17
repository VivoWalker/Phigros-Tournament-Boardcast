# Phigros Tournament Broadcast

用於 Phigros 比賽的本機賽事控制系統與 OBS 網頁疊層。提供主控、記分員和主持人選曲面板，可透過同一區域網路中的電腦或 iPad 操作。

本專案衍生自 [ACAHKU Phigros Competition 2026](https://github.com/VivoWalker/ACAHKU-Phigros-Competition-2026)，保留其 Git 提交歷史，並以通用化版本 [`33f44d4`](https://github.com/VivoWalker/ACAHKU-Phigros-Competition-2026/commit/33f44d49174c18b33928a6d1038c26010dfbb3e6) 為起點。本倉庫是獨立衍生倉庫；GitHub 頁面目前沒有自動的 fork 關聯。

## 功能與範圍

- 自訂賽事名稱、曲庫、預選課題、加賽曲、決賽曲、Logo 和主視覺；支援模板匯入／匯出。
- Plan A／B 預選流程、晉級線同分加賽，以及八人雙淘汰賽。
- 六首候選曲、雙方 BAN、滾動抽出兩首比賽曲目及音訊預覽。
- 分數與 Perfect／Good／Bad／Miss／ACC 錄入、統計、賽果確認及總排名。
- 標準模式使用兩首制決賽；ACAHKU 的三首制、專屬 PV 和侵入／淨化特效保留為原預設。
- 各角色使用不同配對碼，主持人僅能抽曲／BAN；OBS 預覽靜音，正式畫面使用全域音量。

此版仍採用既有計分規則與固定八人雙淘汰樹，不支援任意人數或自訂計分公式。模板只保存配置，素材檔案需另行複製或上傳。

## 啟動標準賽事

安裝 **Node.js 24.22.1 或更新的 24.x 版本**，然後在專案根目錄執行：

```sh
npm ci
npm start -- --standard --data-dir ./data-community
```

`--standard` 只初始化新資料夾，已有存檔沿用原本配置。每場比賽使用不同的 `data-名稱/` 資料夾；配對碼、分數、備份及上傳影片皆保存在該資料夾。這些資料夾已被 Git 忽略。

直接執行 `npm start` 仍保留 ACAHKU 新場預設，以相容既有啟動方式。一般新比賽請使用上面的標準模式命令。

終端會顯示三組配對碼及區域網路網址。保持伺服器運行，使用相應配對碼登入：

| 用途 | 本機網址 |
| --- | --- |
| 主控 | http://localhost:3000/control/ |
| 記分員 | http://localhost:3000/scorekeeper/ |
| 主持人選曲 | http://localhost:3000/host/ |
| OBS Browser Source | http://localhost:3000/overlay/live.html |

iPad 請將 `localhost` 換成終端顯示的伺服器區域網路 IP。單畫面模式為每位選手各一路 4:3 webcam，在 OBS 設為 720 像素高、30 fps。

## 設定與素材

在 **Event & library** 修改賽事資料及曲庫，在 **賽事模板** 選擇兩輪預選加賽曲、兩首決賽曲和品牌圖片。於預選設定中選擇各輪三首課題，核對名單及素材後再選擇 Plan A／B。

模板在預選方案設定或產生賽事紀錄後鎖定。模板不包含選手名單、分數、抽曲／晉級紀錄、配對碼或影片播放進度；賽事中途的保存與恢復請使用完整狀態備份。

圖片使用 `public/assets/` 下的本機路徑，音訊使用 `public/assets/song-preview/`；中場影片可在主控上傳。標準模式不會自動播放內建 Arcaea 預告。匯入模板後，請執行曲庫與素材檢查。

- [通用賽事設定、模板及限制](docs/reusable-events.md)
- [ACAHKU 2026 預設完整操作手冊](docs/acahku-2026.md)
- [人工測試存檔與檢查清單](test/manual-saves/README.md)

## 驗證

```sh
npm test
node --test test/event-templates.test.js
python3 scripts/test-regressions.py --suite browser-smoke --only event-templates-browser
```

瀏覽器測試需要 `requirements-test.txt` 中的依賴及 Chromium；可用 `CHROME_BINARY` 指定已安裝的瀏覽器。測試使用臨時賽事資料，報告寫入 `test-results/`。

## 上游與版本管理

新倉庫的 `origin` 為本專案；上游為原 ACAHKU 倉庫。新 clone 若需追蹤上游，可執行：

```sh
git remote add upstream https://github.com/VivoWalker/ACAHKU-Phigros-Competition-2026.git
git fetch upstream
```

後續功能在本倉庫建立分支與 PR；同步上游修復時，先核對通用模式與 ACAHKU 預設的相容性。完整提交歷史可用於追溯來源及比較變更。
