# Gemini Computer use

Starter code for getting started with Gemini Computer Use models and Playwright for browser automation tasks such as web navigation, reading information, and automated form-filling.

### Overview

This folder contains boilerplate code to:
- Use Google's Gemini Computer Use models for web automation.
- Integrate with Playwright for controlled browser interactions.
- Automate real-world tasks like scraping information or filling out online forms.

### Getting started

1. Clone the repository:

```bash
git clone https://github.com/Ruthvik-1411/computer_use_boilerplates.git
cd computer_use_boilerplates/gemini_computer_use
```
2. Setup the environment variables by copying the contents of `env.example` to `.env`. Make sure to add in the required variables as they will be needed.

```bash
cp env.example .env
```

3. Install dependencies:

You can use either `uv` (recommended for speed) or just `pip` to install dependencies.

**Using uv**

```bash
# Install uv if not already installed
pip install uv

# 1. Create a virtual environment
uv venv

# 2. Activate the virtual environment (Linux/Mac)
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Run the next two commands
# 3. Sync base dependencies
uv sync

# 4. Sync the gemini-computer-use dependency group
uv sync --group gemini-computer-use

# (Optional)
# 3. Install dependencies from requirements.txt incase of issues with uv groups
uv pip install -r requirements.txt
```
**Using pip**

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Linux/Mac)
source .venv/bin/activate
# (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

4. Run playwright setup (required once)
    
```bash
# This might take a while
playwright install chromium
```

### CLI Usage Examples

#### Example 1: Reading data from a webpage

Pass a URL and a query to the agent to extract or summarize data.

```bash
python main.py "What is today's featured article on wikipedia about?" --url "https://en.wikipedia.org/wiki/Main_Page"
```

#### Example 2: Automated form filling

Use the Computer Use agent to fill and submit online forms.

Make sure the `INITIAL_URL` in `config.py` points to your form (e.g., a Google Form).

```bash
python main.py "Fill in the opt-out form for marketing mails. Name is Ruths, email is ruths@email.com, I'm receiving too many emails, but I still want to receive security updates and confirm the data and submit the form."
```

### API Usage Example

[Work in Progress]