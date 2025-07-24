# Silentnight - ScrapeGraphAI Project

This project contains scripts for scraping images of product in a category in Silentnight.ae using ScrapeGraphAI, a powerful AI-powered scraping library.

## Table of Contents

- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Requirements](#requirements)
  - [Virtual Environment Setup](#virtual-environment-setup)
  - [Installing ScrapeGraphAI](#installing-scrapegraphai)
- [OpenRouter Configuration](#openrouter-configuration)
- [Scripts](#scripts)
  - [Basic Scraper (smart_scraper_examples.py)](#basic-scraper-smart_scraper_examplespy)
  - [Multi-Level Scraper (multi_level_scraper.py)](#multi-level-scraper-multi_level_scraperpy)
- [URL Filtering](#url-filtering)
- [Image Processing](#image-processing)
- [Reporting and Tracking](#reporting-and-tracking)
- [Command Line Options](#command-line-options)
- [Usage Examples](#usage-examples)

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)
- Internet access for API calls

### Requirements

This project requires the following Python packages:

```
scrapegraphai>=1.61.0  # Core library for AI-powered web scraping
requests>=2.32.0       # For HTTP requests and downloading images
Pillow>=11.0.0         # For image processing and size checking
```

You can install all required packages using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or install them individually:

```bash
pip install scrapegraphai requests Pillow
```

#### Requirements.txt

Create a file named `requirements.txt` with the following content:

```
scrapegraphai>=1.61.0
requests>=2.32.0
Pillow>=11.0.0
```

### Virtual Environment Setup

It's recommended to use a virtual environment to avoid package conflicts.

#### Windows

```powershell
# Navigate to your project directory
cd your-project-directory

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Verify Python is using the virtual environment
python --version
where python  # Should show the venv path first

# Install requirements
pip install -r requirements.txt
```

#### Linux/Mac

```bash
# Navigate to your project directory
cd your-project-directory

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Verify Python is using the virtual environment
python --version
which python  # Should show the venv path

# Install requirements
pip install -r requirements.txt
```

### Installing ScrapeGraphAI

If not using requirements.txt, you can install ScrapeGraphAI and its dependencies:

```bash
pip install --upgrade pip
pip install scrapegraphai Pillow requests
```

The script requires these additional libraries:
- `requests`: For HTTP requests and downloading images
- `Pillow` (PIL): For image size checking

## OpenRouter Configuration

This project uses OpenRouter to access various LLMs. You'll need an API key:

1. Create an account at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Replace the placeholder API key in the scripts:
   ```python
   OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
   ```

The scripts are configured to use `openai/gpt-4o` by default. You can change this to any model supported by OpenRouter by updating the `model` field.

## Scripts

### Basic Scraper (smart_scraper_examples.py)

This script provides an interactive interface to scrape one or more URLs with a custom prompt.

```
python smart_scraper_examples.py
```

You'll be prompted for:
1. Your query prompt (e.g., "Extract product image links")
2. One or more URLs to scrape (comma-separated)

The script will process each URL and return the results.

### Multi-Level Scraper (multi_level_scraper.py)

This script performs two-level scraping:
1. First level: Extract product URLs from category pages
2. Second level: Extract product images from each product page

```
python multi_level_scraper.py [--force] [--min-size SIZE]
```

Before running, add category URLs to `category_urls.txt` (one URL per line).

**Features:**

- **Category Name Extraction**: Creates folder names from category URLs (e.g., "all-pillows" instead of "category_1")
- **URL Normalization**: Correctly handles relative URLs by converting them to absolute
- **Image Size Filtering**: Only downloads images larger than specified size (default: 301x301 pixels)
- **Smart URL Filtering**: Only processes product URLs that belong to the current category
- **Progress Tracking**: Keeps track of processed items to avoid redundant work
- **Reporting**: Generates detailed reports of scraping results

Output is organized in the following structure:
```
scraped_products/
├── category-name-1/
│   ├── Product_Name_1/
│   │   ├── image_1.jpg
│   │   └── image_2.jpg
│   └── Product_Name_2/
│       ├── image_1.jpg
│       └── image_2.jpg
└── category-name-2/
    ...
```

## URL Filtering

The multi-level scraper includes intelligent URL filtering to ensure only relevant product URLs are processed:

- **Category-specific filtering**: Only product URLs that belong to the current category are processed
- **Pattern recognition**: Automatically identifies product URLs based on common patterns like `/products/`, `/product/`, etc.
- **Domain checking**: Ensures URLs are from the same domain as the category page
- **URL structure validation**: Specifically handles e-commerce site structures like those on Silentnight.ae

For example, if scraping `https://www.silentnight.ae/collections/all-pillows`, the scraper will:
- ✅ Include: `https://www.silentnight.ae/collections/all-pillows/products/luxury-micro-fibre-pillow-silver-piping`
- ❌ Exclude: `https://www.silentnight.ae/collections/other-category/products/some-product`
- ❌ Exclude: Non-product links like category navigation, homepage links, etc.

The filtering logic ensures you only get products that belong to the category you're scraping, making the results more accurate and avoiding duplicate content.

## Image Processing

The multi-level scraper includes image processing features:

- **Size Detection**: Checks image dimensions before downloading
- **Size Filtering**: Only downloads images larger than specified size (default: 301x301 pixels)
- **Format Handling**: Automatically detects image formats from URLs
- **Size Reporting**: Displays dimensions of downloaded images

This ensures your scraped data only contains high-quality images suitable for your needs, saving storage space and processing time.

## Reporting and Tracking

The multi-level scraper generates comprehensive reports and tracks progress:

### Reporting

A `scraping_report.txt` file is generated in the project directory with the following information:
- **Summary**: Total categories, products, images found and downloaded
- **Categories**: List of all categories scraped with product and image counts
- **Products**: List of all products organized by category
- **Failed Images**: List of images that couldn't be downloaded with failure reasons

### Progress Tracking

The script creates a `processed_items.json` file that keeps track of:
- **Processed Categories**: Categories that have already been processed
- **Processed Products**: Products that have already been processed
- **Processing Dates**: When each item was last processed
- **Statistics**: Number of images found and downloaded for each product

This tracking enables:
- **Skip Already Processed**: Avoid redundant scraping of previously processed items
- **Resume Scraping**: Continue from where you left off if the script is interrupted
- **Force Reprocessing**: Option to reprocess items when needed

## Command Line Options

The multi-level scraper supports the following command line options:

```
python multi_level_scraper.py [options]
```

- `--force`: Force reprocessing of already processed items
- `--min-size SIZE`: Set minimum image size in pixels (both width and height, default: 301)

Examples:
```bash
# Use default settings
python multi_level_scraper.py

# Force reprocessing of all items
python multi_level_scraper.py --force

# Only download images at least 500x500 pixels
python multi_level_scraper.py --min-size 500

# Force reprocessing and set minimum size
python multi_level_scraper.py --force --min-size 400
```

## Usage Examples

### Example 1: Extract product images from a single page

```
> python smart_scraper_examples.py
Enter your prompt: extract product image links of this product page
Enter one or more URLs, separated by commas: https://www.example.com/products/sample-product

Scraping: https://www.example.com/products/sample-product
Result: {'content': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']}
```

### Example 2: Multi-level scraping of an e-commerce category

1. Create or edit `category_urls.txt`:
   ```
   https://www.silentnight.ae/collections/all-pillows
   https://www.example.com/collections/bedding
   ```

2. Run the script:
   ```
   > python multi_level_scraper.py
   ```

3. The script will:
   - Extract all product URLs from each category
   - Filter out URLs that don't belong to the current category
   - Process each product page to extract product name and images
   - Skip images smaller than the specified size
   - Download all product images into organized folders named after the categories
   - Generate a comprehensive report of the results
   - Track progress to avoid redundant processing in future runs

## Troubleshooting

- **ModuleNotFoundError**: Make sure your virtual environment is activated and dependencies are installed.
- **API Errors**: Check your OpenRouter API key and model selection.
- **Rate Limiting**: Adjust the sleep timers in the script if you encounter rate limiting.
- **Image Download Failures**: Some sites may block automated downloads. Check the URLs and consider adjusting headers.
- **URL Filtering Issues**: If you notice incorrect filtering, you may need to adjust the `is_product_url_in_category` function to match your site's URL structure.
- **Image Size Issues**: If too many images are being skipped, you can adjust the minimum image size with the `--min-size` parameter.
- **Already Processed Items**: If you want to reprocess items, use the `--force` parameter or delete the `processed_items.json` file.

## License

This project is for educational purposes only. Be sure to respect websites' terms of service and robots.txt files when scraping. 