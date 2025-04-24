# IGController

**IGController** is a Python-based tool for managing and automating Instagram accounts, now fully controlled via a Telegram bot. It provides a structured approach to interact with Instagram's API and automate common tasks such as posting and user interaction.

---

## 🚀 Features

- 📱 Instagram account management
- 🤖 Automated posting and interaction via Telegram bot
- ⚙️ Configurable through environment variables
- 🧩 Modular architecture with handlers and helpers

---

## 🧾 Project Structure


```
IGController/
├── .gitignore           # Git ignore file
├── README.md            # This documentation
├── config.py            # Configuration and environment variable handling
├── main.py              # Main entry point
├── requirements.txt     # Project dependencies
└── src/                 # Source code
    ├── handlers/        # Request handlers
    │   ├── bot/         # Bot-related handlers
    │   └── ig/          # Instagram-specific handlers
    ├── helpers/         # Helper functions
    │   ├── bot/         # Bot helper utilities
    │   └── ig/          # Instagram helper utilities
    └── plugins/         # Plugin system for extensions
```

---

## 🛠 Installation

### ✅ Prerequisites

- Python 3.6+
- Instagram account credentials

### 📦 Setup

Clone the repository:

```bash
git clone https://github.com/usif-x/IGController.git
cd IGController
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory with your Instagram credentials:

```env
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
```

---

## ▶️ Usage

Run the main script to start the controller:

```bash
python main.py
```

---

## ⚙️ Configuration

The application uses environment variables for configuration, loaded from a `.env` file. Key variables include:

- `IG_USERNAME`: Your Instagram username
- `IG_PASSWORD`: Your Instagram password

---

## 🧑‍💻 Development

The project follows a modular structure for ease of extension and maintenance:

- `handlers/`: Logic for handling requests
- `helpers/`: Reusable utilities
- `plugins/`: Extensible plugin system

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

---

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Use at your own risk and ensure compliance with Instagram's [Terms of Service](https://help.instagram.com/581066165581870).
