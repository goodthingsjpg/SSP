# 伸手排 SSP（ShenShouPai）

通知單一鍵排版成 A4，支援注音模式。
One-page A4 school notice layout tool with Zhuyin (Bopomofo) support.

![伸手排 畫面截圖](docs/screenshot.png)

---

## 中文說明

### 這是什麼？

老師每週都要發通知單：校外教學、繳費、活動回條……
伸手排讓你把文字貼進去，就自動排成一張 A4，可以直接列印或下載 PDF。
低年級需要注音？打開開關，字旁就會印上注音。

### 功能

- **一頁 A4，自動塞滿**：1 / 2 / 4 / 6 張一頁，字級自動調整到剛好放得下
- **注音模式**：使用王漢宗中楷體注音，字旁直接印注音
- **破音字校正**：自動修正約 250 個常見詞（家長、放假、音樂、中暑……），也可以手動指定：`長(ㄓㄤˇ)`
- **一鍵貼上**：用「標題：／內容：／回條：／署名：」格式貼上，自動分欄
- **回條勾選框**：輸入 `[]` 會變成 ☐
- **下載 PDF / 直接列印**
- **免安裝、可離線**：另有字型全部內嵌的離線單檔版

### 怎麼用

**線上使用**：打開 https://goodthingsjpg.github.io/SSP/ 即可。
打開注音模式時，只會下載這張通知單用得到的字（一般通知單約 1MB），之後瀏覽器會記住，就不用再等。

**離線使用**：下載 `ssp-offline.html`，用 Chrome 開啟。字型已全部內嵌，沒有網路也能用。

> 💡 列印時選「A4、縮放 100%、邊界：無」。

### 破音字小提醒

注音字型裡每個字只有一種讀音。工具已內建常見詞的校正，左側面板會列出這次改了哪些字。
如果還是讀錯，在字後面加括號注音即可（全形、半形括號都可以）：

```
親愛的家長(ㄓㄤˇ)您好      → 長 讀 ㄓㄤˇ
我們一起學了(˙ㄌㄜ)很多     → 輕聲寫在最前面
```

詞庫位於 `src/template.html` 的 `POLYPHONE_DICT`，歡迎發 PR 補充。

---

## English

### What is it?

SSP — ShenShouPai (伸手排, "reach out and it’s laid out") is a single-file web tool that lays out school notices (通知單) on one A4 page for Taiwanese teachers.
Paste the text, choose 1 / 2 / 4 / 6 copies per page, and print or download a PDF.
Zhuyin mode prints Bopomofo next to every character for young readers.

### Features

- Auto-fit font size so each copy fills its slot on one A4 page
- Zhuyin mode using the HanWang Kai Medium ChuIn font
- Polyphone correction: ~250 built-in phrases, plus manual override syntax `字(ㄓㄨˋ)`
- PDF download and direct printing
- Online version loads fonts on demand; a fully self-contained offline file is also provided

---

## 開發 Development

`index.html`、`ssp-offline.html`、`assets/` 都是建置產物。要修改請編輯 `src/template.html`，再重新建置：

```bash
pip install fonttools brotli
npm install
npm run build        # → index.html + assets/ + ssp-offline.html
```

| 路徑 | 說明 |
|---|---|
| `src/template.html` | 主程式（HTML / CSS / JS） |
| `tools/build.py` | 產生網頁版 `index.html`（字型依字頻切成小塊放 `assets/`）與離線單檔版 `ssp-offline.html` |
| `tools/build_plain.py` | 從注音字型抽出「不含注音」的楷體字形，用於破音字校正 |
| `tools/char_freq_tw.txt` | 繁體中文字頻表（常用字在前），用來把字型切成小塊 |
| `tools/plain_chars.txt` | 楷體子集的字表（Big5 常用字 + 破音字） |
| `fonts/` | 王漢宗中楷體注音原始字型 |

---

## 授權 License

本專案以 **GPL-3.0-or-later** 授權釋出，詳見 [LICENSE](LICENSE)。

This project is licensed under **GPL-3.0-or-later**.

### 第三方元件 Third-party

| 元件 | 作者 | 授權 |
|---|---|---|
| 王漢宗中楷體注音 HanWangKaiMediumChuIn | 王漢宗 Dr. Hann-Tzong Wang | GPL-2.0-or-later |
| [jsPDF](https://github.com/parallax/jsPDF) 2.5.2 | parallax | MIT |
| [modern-screenshot](https://github.com/qq15725/modern-screenshot) 4.7.0 | qq15725 | MIT |
| [Tailwind CSS](https://tailwindcss.com) 3.4 | Tailwind Labs | MIT |
| [Noto Sans TC](https://fonts.google.com/noto/specimen/Noto+Sans+TC)（線上載入） | Google | OFL-1.1 |

字型版權隸屬王漢宗先生，依 GPL 授權使用與散布；`assets/` 與 `ssp-offline.html` 內的字型為原始字型轉檔與子集化的衍生版本，原始字型檔收錄於 `fonts/`。

---

made with ♡ by goodthings.jpg 2026.10
