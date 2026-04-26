# StepWise: Algorithmic Thinking Mentor

**StepWise** is an interactive, AI-powered educational tool designed for 5th-grade students to master the fundamentals of algorithmic thinking. Using the cutting-edge **Gemini 2.5 Flash** model, StepWise acts as a friendly mentor that guides students through logic, flowcharts, and problem-solving steps.

## Live Demo on Hugging Face: https://huggingface.co/spaces/Fatser/StepWise
## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** Python 3.9+
- **LLM API:** Google Generative AI (Gemini 2.5 Series)
- **Configuration:** Python-dotenv

---

## 🚀 Getting Started

Follow these steps to get your local copy up and running:

### 1. Prerequisites

Ensure you have Python installed. You can check by running:

```bash
python --version
```

### 2. Installation

Clone the repository and enter the directory:

```bash
git clone https://github.com/ibahars/StepWise.git
cd StepWise
```

### 3. Setup Virtual Environment

It is recommended to use a virtual environment:

```bash
# Create environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Mac/Linux)
source .venv/bin/activate
```

### 4. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 5. API Configuration

Create a `.env` file in the root folder and add your Gemini API Key:

### 6. Run the App

Launch the Streamlit interface:

```bash
streamlit run main.py
```

---

## 📂 Project Structure

- `main.py`: The core application logic and UI.
- `prompts.py`: System instructions and educational content guidelines.
- `.env`: Local environment variables (API keys).
