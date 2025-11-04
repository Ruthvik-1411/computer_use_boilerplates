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

2. Set up the environment variables for gemini_computer_use by copying the example file and filling in your configuration.
```bash
cp env.example .env
```
Modify the .env file and configure one of the two supported authentication methods below:

**A. Using Gemini API key (Developer access):**

If you’re using a Google AI Studio / Gemini API key, set it like this:
```bash
GEMINI_API_KEY="your-google-api-key"
USE_VERTEXAI=false
```
This method uses the developer Gemini API directly and hit's the developer endpoints via the provided API key. No additional GCP setup is required.

**B. Use Vertex AI with Application Default Credentials (ADC):**

If you prefer to use Vertex AI endpoints and have a GCP project configured, enable Vertex AI and specify your project and region:
```bash
USE_VERTEXAI=true
VERTEXAI_PROJECT="gcp-project-id"
# Note: Change location to "global" as some models might be preview and not GA in other regions
VERTEXAI_LOCATION="us-central1"
```


4. Run playwright setup (required once)
    
```bash
# This might take a while
playwright install chromium
```

### CLI Usage

The `main.py` script is the command-line interface (CLI) for running the computer use agent. The agent can be run both synchronously [`run_agent_sync`](main.py#L14) and asynchronously [`run_agent_async`](main.py#L43).

**CLI Arguments:**

| Argument | Description | Required | Default |
|-|-|-|-|
| `--goal` | The goal for the computer use agent to achieve. | Yes | - |
| `--initial_url` | The initial URL/page to load when the browser starts. | No | https://www.google.com |

#### Example 1: Reading data from a webpage

Pass a URL and a query to the agent to extract or summarize data.

```bash
python main.py --goal="What is today's featured article on wikipedia about?" --initial_url "https://en.wikipedia.org/wiki/Main_Page"
```

#### Example 2: Automated form filling

Use the Computer Use agent to fill and submit online forms.

Make sure the `INITIAL_URL` in `config.py` points to your form (e.g., a Google Form).

```bash
python main.py --goal="Fill in the opt-out form for marketing mails. Name is Peter, email is p.parker@email.com, I'm receiving too many emails, but I still want to receive security updates. Confirm the data and submit the form."
```

### API Usage

The agent can also be exposed as a REST API. The relevant implementation can be found in:
- `server.py` – the entry point for starting the API server
- `api/main.py` – FastAPI application setup
- `api/routes.py` – endpoint definitions

### Starting the server
Start the FastAPI server using:

```bash
python server.py
```

This will start the server at [http://localhost:8090](http://localhost:8090).

Once the server is running, open [http://localhost:8090/v1/api/docs](http://localhost:8090/v1/api/docs) in the browser to see the **Swagger UI** and explore the available endpoints.

### Available Endpoints

- Synchronous Agent:
    - Try the [`/run_agent_sync`](api/routes.py#L38) on Swagger UI.
    - Use the prefilled values and `Try it out` or provide values as needed similar to [Example: Reading data from a webpage](#example-1-reading-data-from-a-webpage)

- Asynchronous Agent:
    - Try the [`/run_agent_async`](api/routes.py#L72) on Swagger UI in a similar way.

