install.md
# ⚙️ Installation

## Requirements
- Python 3.10+  
- `pip` package manager  
- Internet connection to an XRPL node (public or private)

## 1. Clone the repository
```bash
git clone https://github.com/terramike/grid-wizard.git
cd grid-wizard

2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Configure your environment

Copy the example file and edit your wallet info:

cp examples/.env.example .env


⚠️ Never commit .env — it contains private keys.
.gitignore already protects it.
