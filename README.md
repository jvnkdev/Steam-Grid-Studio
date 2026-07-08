# 🎨 Steam Grid Studio

Generate custom Steam library artwork — grids, hero banners & logos — for your games in seconds.

Steam Grid Studio is a Python tool that creates custom Steam library artwork — capsule grids, hero banners, and logos — for any game in your library. Pick a style template (retro CRT, minimal, neon, and more), point it at a game, and get ready-to-use Steam-sized assets without touching Photoshop or GIMP.

Pairs well with [Steam-Startup-Movies](https://github.com/MRJeffyy/Steam-Startup-Movies) if you're into fully customizing your Steam Big Picture experience.

## ✨ Features

- 🖼️ Generate all standard Steam asset sizes (capsule grid, hero banner, logo)
- 🎭 Multiple built-in style templates (retro CRT, minimal, neon, and more)
- ⚡ Fast, simple CLI — no image editing skills required
- 🧩 Works with any game name or source image
- 🛠️ Easy to extend with your own custom templates

## 📦 Installation

```bash
git clone https://github.com/MRJeffyy/Steam-Grid-Studio.git
cd Steam-Grid-Studio
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python steamgrid.py --game "Half-Life 2" --style retro
```

**Options:**

| Flag | Description |
|------|-------------|
| `--game` | Name of the game |
| `--style` | Style template to use (`retro`, `minimal`, `neon`, ...) |
| `--input` | Optional source image to base the artwork on |
| `--output` | Output folder (default: `./output`) |

## 🖌️ Style Templates

- **Retro** — CRT scanlines & glitch aesthetic
- **Minimal** — Clean, flat design
- **Neon** — Vibrant cyberpunk-style glow

## 📁 Output Sizes

| Asset | Size |
|-------|------|
| Grid Capsule | 600x900 |
| Hero Banner | 1920x620 |
| Logo | 1280x720 |

## 🤝 Contributing

Contributions, ideas, and new style templates are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
