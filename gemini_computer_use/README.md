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
cd computer_use_boilerplates
```

2. Install dependencies:

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

# 3. Sync base dependencies
uv sync

# 4. Sync the gemini-computer-use dependency group
uv sync --group gemini-computer-use

# 5. Navigate to gemini_computer_use folder
cd gemini_computer_use

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

# 5. Navigate to gemini_computer_use folder
cd gemini_computer_use

# Install dependencies
pip install -r requirements.txt
```

2. Setup the environment variables for `gemini_computer_use` by copying the contents of `env.example` to `.env`. Make sure to add in the required variables as they will be needed.

```bash
cp env.example .env
```

4. Run playwright setup (required once)
    
```bash
# This might take a while
playwright install chromium
```

### CLI Usage

The agent can be run using the cli using:
```bash
python main.py "Goal"
# or
python main.py "Goal" --url "initial_url"
```

#### Example 1: Reading data from a webpage

Pass a URL and a query to the agent to extract or summarize data.

```bash
python main.py "What is today's featured article on wikipedia about?" --url "https://en.wikipedia.org/wiki/Main_Page"
```

#### Example 2: Automated form filling

Use the Computer Use agent to fill and submit online forms.

Make sure the `INITIAL_URL` in `config.py` points to your form (e.g., a Google Form).

```bash
python main.py "Fill in the opt-out form for marketing mails. Name is Peter, email is p.parker@email.com, I'm receiving too many emails, but I still want to receive security updates. Confirm the data and submit the form."
```

### API Usage

The agent can also be exposed as a REST API. The relevant code can be found in `server.py`, `api/main.py` and `api/routes.py`.

### Starting the server
Start the FastAPI server using:

```bash
python server.py
```

This will serve the API at [http://localhost:8090](http://localhost:8090).

Once the server is running, open [http://localhost:8090/v1/api/docs](http://localhost:8090/v1/api/docs) in the browser to see the Swagger UI.

Try out the synchronous API `/run_agent_sync` with the required fields similar to [Example: Reading data from a webpage](#example-1-reading-data-from-a-webpage) on the swagger UI.

> Note: The API runs synchronously for now i.e. each call will block until the agent finishes. So, other concurrent calls will be blocked until the existing processes finish. Conversion to async playwright is in progress.
