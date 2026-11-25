# ChandRush Comic Project & ChandRush Studio

This repository hosts the **ChandRush** mathematics graphic novel comic pipeline and **ChandRush Studio**, a desktop UI application to manage comic production runs, review gates, and page editing.

---

## Building ChandRush Studio AppImage from GitHub

Follow these steps to build `/home/abhay/F/Freelance/Ankush-Project/studio/dist/ChandRush Studio-0.1.0.AppImage` directly from GitHub:

### 1. Prerequisites
Ensure you have the following installed on your Linux system:
- **Node.js**: `v20.x` or higher and `npm` (`node -v` & `npm -v`)
- **Git**
- **Python 3** with `Pillow` (`pip install pillow`)
- **Firefox** (headless PDF rendering)
- **Claude CLI**: installed and authenticated (`claude login`)

### 2. Clone the Repository
Clone the repository and checkout the active branch:
```bash
git clone https://github.com/akashch1013/Ankush-Project.git
cd Ankush-Project
git checkout token-efficient-runs
```

### 3. Navigate to Studio
```bash
cd studio
```

### 4. Install Dependencies
```bash
npm install
```

### 5. Build the Linux AppImage
```bash
npm run dist:linux
```
This command compiles the Electron backend and React frontend via `electron-vite build` and packages the application with `electron-builder --linux AppImage`.

### 6. Generated AppImage Binary
Upon completion, the AppImage is located at:
```text
studio/dist/ChandRush Studio-0.1.0.AppImage
```
(Full path: `/home/abhay/F/Freelance/Ankush-Project/studio/dist/ChandRush Studio-0.1.0.AppImage`)

### 7. Running the AppImage
```bash
chmod +x "studio/dist/ChandRush Studio-0.1.0.AppImage"
./"studio/dist/ChandRush Studio-0.1.0.AppImage"
```
*Note: In environments where user sandboxing is restricted, add the `--no-sandbox` flag:*
```bash
./"studio/dist/ChandRush Studio-0.1.0.AppImage" --no-sandbox
```

---

## Repository Structure

- `studio/`: Electron + React desktop application (ChandRush Studio).
  - See [studio/README.md](file:///home/abhay/F/Freelance/Ankush-Project/studio/README.md) for details on architecture, board controls, and review gates.
- `Tasks/`: Production comic pipeline (manuscripts, backgrounds, panel art, page sheets, PDF rendering).
  - See [CLAUDE.md](file:///home/abhay/F/Freelance/Ankush-Project/CLAUDE.md) and [Tasks/CLAUDE.md](file:///home/abhay/F/Freelance/Ankush-Project/Tasks/CLAUDE.md) for comic master agent instructions.
