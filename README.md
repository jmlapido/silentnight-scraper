# Silentnight Scraper

A multi-level web scraper for extracting product names and images from Silentnight (and similar) e-commerce sites. Uses LLM-powered extraction via OpenRouter and ScrapegraphAI.

## Features
- Scrapes product names and images from category and product pages
- Downloads images above a minimum size
- Avoids reprocessing already-scraped items
- Generates a summary report
- Uses OpenRouter for LLM-powered extraction (configurable)

## Requirements
- Python 3.8+
- [OpenRouter API key](https://openrouter.ai/)
- See `requirements.txt` for dependencies

## Setup

1. **Clone the repository**

```sh
git clone https://github.com/jmlapido/silentnight-scraper.git
cd silentnight-scraper
```

2. **Install dependencies**

```sh
pip install -r requirements.txt
```

> **Note:**
> This project uses [python-dotenv](https://pypi.org/project/python-dotenv/) to automatically load environment variables from a `.env` file if present. If you use a `.env` file, it will be loaded automatically—no manual code changes needed. If you install dependencies via `requirements.txt`, `python-dotenv` will be installed. If not, you can install it manually with:
> ```sh
> pip install python-dotenv
> ```

3. **Configure your OpenRouter API key**

You can provide your OpenRouter credentials in a `.env` file (recommended) or as environment variables.

### .env file example
Create a file named `.env` in the project root with the following content:

```
OPENROUTER_API_KEY=your-openrouter-key-here
OPENAI_API_KEY=your-openrouter-key-here
OPENAI_API_BASE=https://openrouter.ai/api/v1
```

- `OPENROUTER_API_KEY` and `OPENAI_API_KEY` should be set to your OpenRouter API key.
- `OPENAI_API_BASE` should be set to `https://openrouter.ai/api/v1` for OpenRouter.

Alternatively, you can set these variables in your shell before running the script:

**Windows PowerShell:**
```powershell
$env:OPENROUTER_API_KEY="your-openrouter-key-here"
$env:OPENAI_API_KEY="your-openrouter-key-here"
$env:OPENAI_API_BASE="https://openrouter.ai/api/v1"
```

**Linux/macOS Bash:**
```bash
export OPENROUTER_API_KEY="your-openrouter-key-here"
export OPENAI_API_KEY="your-openrouter-key-here"
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
```

4. **Add category URLs**

Edit `category_urls.txt` and add one category/listing page URL per line (no quotes, no commas).

5. **Run the scraper**

```sh
python multi_level_scraper.py --min-size 300
```

## Notes
- The script will use the environment variables if set, otherwise fallback to the hardcoded key in the script.
- Images smaller than the specified minimum size will be skipped.
- Results are saved in the `scraped_products/` directory.
- A summary report is generated as `scraping_report.txt`.

## License
MIT 