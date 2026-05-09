# 🥦 FreshMate — Your Digital Pantry Manager

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![wxPython](https://img.shields.io/badge/GUI-wxPython-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

> **FreshMate** is a lightweight desktop app built with wxPython that helps you manage your pantry, track food expiry dates, and discover recipes — so you waste less and cook smarter.

---

## 📸 Screenshot

<img width="1105" height="815" alt="Screenshot 2026-05-09 145107" src="https://github.com/user-attachments/assets/fa5de8cd-cb13-422e-ac6c-f334cb9ff417" />

---

## ✨ Features

- 📦 **Pantry Tracking** — Add grocery items with their purchase dates and auto-calculated expiry dates
- ⏰ **Expiry Alerts** — Check which items are expiring soon or have already expired within a configurable day range
- 🍳 **Recipe Suggestions** — See all recipes you can make right now based on the ingredients currently in your pantry
- 🗂️ **Purchase History** — Keeps a running log of your latest purchase per item
- 🧹 **Easy Management** — Clear your purchases file and start fresh anytime
- 💾 **Persistent Storage** — Data is saved locally so your pantry is always remembered between sessions

---

## 🖥️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language  | Python 3.x |
| GUI Framework | [wxPython](https://wxpython.org/) |
| Data Storage | Local file (CSV / JSON) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- wxPython

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/freshmate.git
   cd freshmate
   ```

2. **Install dependencies**
   ```bash
   pip install wxpython
   ```

3. **Run the app**
   ```bash
   python freshmate.py
   ```

---

## 🧭 How to Use

### ➕ Adding a Purchase
1. Type the item name in the **Item** field (or select from the dropdown)
2. Set the **Purchase Date** (defaults to today)
3. Click **Add & Save** — the item is added to your pantry

### 🔍 Checking Expiry
1. Set a **Check Date** and the **Within Days** range
2. Click **Check Expiring Items**
3. View results split across three panels:
   - **Expiring Items (soon)** — items nearing their expiry
   - **Expired Items** — items already past their date
   - **Recipes You Can Make** — recipes where all ingredients are present in your pantry

### 🗑️ Clearing Data
- Click **Clear Purchases File** to wipe all stored pantry data and start fresh

---

## 📁 Project Structure

```
freshmate/
│
├── freshmate.py          # Main application entry point
├── purchases.csv         # Local data store for pantry items
├── recipes.json          # Recipe definitions with ingredients
├── README.md
└── screenshot.png
```

---

## 🌱 Why FreshMate?

Every year, millions of tons of food are wasted simply because people forget what they have or don't know what to cook with it. FreshMate solves this by putting your pantry right on your desktop — keeping you informed, reducing waste, and making meal planning effortless.

---

## 🛠️ Roadmap

- [ ] Barcode scanning support
- [ ] Notification/reminder system for expiring items
- [ ] Expanded recipe database
- [ ] Export pantry report to PDF
- [ ] Dark mode UI

---

