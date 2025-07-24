import os
import requests
import time
import re
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin
from io import BytesIO
from PIL import Image
from scrapegraphai.graphs import SmartScraperGraph

# Replace with your actual OpenRouter API key
OPENROUTER_API_KEY = "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"

llm_config = {
    "api_key": OPENROUTER_API_KEY,
    "base_url": "https://openrouter.ai/api/v1",
    "model": "openai/gpt-4o-mini",
    "temperature": 0,
}

# Global report data
report_data = {
    "timestamp": "",
    "categories": [],
    "total_products": 0,
    "total_images_found": 0,
    "total_images_downloaded": 0,
    "total_images_skipped": 0,
    "failed_urls": []
}

# File paths
PROCESSED_LOG_FILE = "processed_items.json"
REPORT_FILE = "scraping_report.txt"

def sanitize_filename(name):
    """Create a safe filename from a string"""
    return ''.join(c for c in name if c.isalnum() or c in ' _-')[:50].strip().replace(' ', '_')

def get_image_size(image_url):
    """Get the size of an image from its URL"""
    # Ensure URL is absolute
    if image_url.startswith('//'):
        image_url = 'https:' + image_url
        
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code == 200:
            # Read the image data into memory
            img_data = BytesIO(response.content)
            # Open the image with PIL
            img = Image.open(img_data)
            # Return the width and height
            return img.size
        else:
            return (0, 0)
    except Exception as e:
        print(f"  Error checking image size for {image_url}: {e}")
        return (0, 0)

def download_image(url, folder_path, filename, min_size=(100, 100)):
    """Download image from URL to specified folder if it meets minimum size requirements"""
    # Ensure URL is absolute
    if url.startswith('//'):
        url = 'https:' + url
    
    try:
        # Check image size first
        width, height = get_image_size(url)
        
        # Skip if image is too small
        if width < min_size[0] or height < min_size[1]:
            print(f"  Skipping small image ({width}x{height}): {url}")
            report_data["total_images_skipped"] += 1
            report_data["failed_urls"].append({"url": url, "reason": f"Image too small ({width}x{height})"})
            return False
        
        # Download the image
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Create folder if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)
            
            # Save the image
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"  Downloaded: {filename} ({width}x{height})")
            report_data["total_images_downloaded"] += 1
            return True
        else:
            print(f"  Failed to download ({response.status_code}): {url}")
            report_data["total_images_skipped"] += 1
            report_data["failed_urls"].append({"url": url, "reason": f"HTTP error {response.status_code}"})
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        report_data["total_images_skipped"] += 1
        report_data["failed_urls"].append({"url": url, "reason": str(e)})
    return False

def create_category_urls_file():
    """Create a sample category_urls.txt file if it doesn't exist"""
    if not os.path.exists('category_urls.txt'):
        with open('category_urls.txt', 'w') as f:
            f.write("# Add your category/listing page URLs below (one per line)\n")
            f.write("# Example: https://www.silentnight.ae/collections/all-pillows\n")
            f.write("# Example: https://www.example.com/collections/bedding\n")
        print("Created 'category_urls.txt'. Please add your category URLs to this file (one per line).")
        return False
    return True

def load_processed_items():
    """Load previously processed products and categories"""
    if os.path.exists(PROCESSED_LOG_FILE):
        try:
            with open(PROCESSED_LOG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading processed items: {e}")
    
    # Return empty structure if file doesn't exist or there's an error
    return {
        "processed_categories": {},
        "processed_products": {}
    }

def save_processed_items(processed_data):
    """Save processed products and categories to JSON file"""
    with open(PROCESSED_LOG_FILE, 'w') as f:
        json.dump(processed_data, f, indent=2)
    print(f"Saved processed items to {PROCESSED_LOG_FILE}")

def generate_report():
    """Generate a human-readable report"""
    report_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(REPORT_FILE, 'w') as f:
        f.write(f"# SCRAPING REPORT - {report_data['timestamp']}\n\n")
        
        f.write("## SUMMARY\n")
        f.write(f"- Categories Processed: {len(report_data['categories'])}\n")
        f.write(f"- Total Products Processed: {report_data['total_products']}\n")
        f.write(f"- Total Images Found: {report_data['total_images_found']}\n")
        f.write(f"- Total Images Downloaded: {report_data['total_images_downloaded']}\n")
        f.write(f"- Total Images Skipped: {report_data['total_images_skipped']}\n\n")
        
        f.write("## CATEGORIES\n")
        for cat_data in report_data["categories"]:
            f.write(f"- {cat_data['name']} ({cat_data['url']})\n")
            f.write(f"  - Products: {cat_data['products_processed']}\n")
            f.write(f"  - Images Downloaded: {cat_data['images_downloaded']}\n")
        f.write("\n")
        
        f.write("## PRODUCTS\n")
        for cat_data in report_data["categories"]:
            f.write(f"### {cat_data['name']}\n")
            for product in cat_data["products"]:
                f.write(f"- {product['name']} ({product['url']})\n")
                f.write(f"  - Images Found: {product['images_found']}\n")
                f.write(f"  - Images Downloaded: {product['images_downloaded']}\n")
            f.write("\n")
        
        if report_data["failed_urls"]:
            f.write("## FAILED IMAGES\n")
            for failed in report_data["failed_urls"]:
                f.write(f"- {failed['url']} - {failed['reason']}\n")
    
    print(f"Report generated: {REPORT_FILE}")

def normalize_url(url, base_url):
    """Normalize a URL, converting relative URLs to absolute"""
    # Handle URLs that start with a slash (relative to domain root)
    if url.startswith('/'):
        # Get the base domain
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        return urljoin(base_domain, url)
    # Handle already absolute URLs
    elif url.startswith(('http://', 'https://')):
        return url
    # Handle protocol-relative URLs (//example.com)
    elif url.startswith('//'):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}:{url}"
    # Handle other relative URLs
    else:
        return urljoin(base_url, url)

def extract_category_name(category_url):
    """Extract a readable category name from the URL"""
    # Try to extract a name from collections URL
    collections_match = re.search(r'/collections/([^/]+)', category_url)
    if collections_match:
        return collections_match.group(1)
    
    # Try to extract last meaningful path component
    parsed = urlparse(category_url)
    path_parts = parsed.path.strip('/').split('/')
    if path_parts:
        return path_parts[-1]
    
    # Fall back to domain name if no suitable path components
    return parsed.netloc.replace('.', '_')

def is_product_url_in_category(product_url, category_url):
    """Check if a product URL belongs to the given category"""
    # Normalize URLs
    normalized_product_url = normalize_url(product_url, category_url)
    
    # Strip trailing slashes for consistent comparison
    normalized_product_url = normalized_product_url.strip().rstrip('/')
    category_url = category_url.strip().rstrip('/')
    
    # Parse URLs
    parsed_product = urlparse(normalized_product_url)
    parsed_category = urlparse(category_url)
    
    # Check if same domain
    if parsed_product.netloc != parsed_category.netloc:
        return False
    
    # For Silentnight and similar sites with /collections/ pattern
    if '/collections/' in category_url and '/collections/' in normalized_product_url:
        # Extract the collection name from the category URL
        # e.g., /collections/all-pillows -> all-pillows
        category_match = re.search(r'/collections/([^/]+)', parsed_category.path)
        if category_match:
            collection_name = category_match.group(1)
            
            # Check if the product URL contains this collection name
            # and has the products part in the path
            if f'/collections/{collection_name}/products/' in normalized_product_url:
                return True
    
    # More generic check for nested URLs
    if normalized_product_url.startswith(category_url) and normalized_product_url != category_url:
        # Make sure it's likely a product (contains typical product URL patterns)
        product_indicators = ['/products/', '/product/', '/item/', '/p/']
        return any(indicator in normalized_product_url for indicator in product_indicators)
    
    return False

def filter_product_urls(product_urls, category_url):
    """Filter product URLs to only include those from the current category"""
    filtered_urls = []
    
    for url in product_urls:
        normalized_url = normalize_url(url, category_url)
        if is_product_url_in_category(normalized_url, category_url):
            filtered_urls.append(normalized_url)
        else:
            # Skip URLs that don't match the current category
            print(f"  Skipping non-category URL: {url}")
    
    return filtered_urls

def process_product_page(product_url, product_index, base_output_dir, category_data, processed_data, min_size=301):
    """Process a single product page to extract name and images"""
    print(f"\nProcessing product {product_index}: {product_url}")
    
    # Check if product was already processed
    if product_url in processed_data["processed_products"]:
        product_info = processed_data["processed_products"][product_url]
        print(f"Product already processed: {product_info['name']} ({product_info['images_downloaded']} images)")
        
        # Add to category products list for reporting
        category_data["products"].append({
            "name": product_info["name"],
            "url": product_url,
            "images_found": product_info["images_found"],
            "images_downloaded": product_info["images_downloaded"],
            "skipped": True
        })
        
        # Update counters
        category_data["products_processed"] += 1
        category_data["images_downloaded"] += product_info["images_downloaded"]
        report_data["total_products"] += 1
        report_data["total_images_found"] += product_info["images_found"]
        report_data["total_images_downloaded"] += product_info["images_downloaded"]
        
        return product_info["name"], product_info["images_downloaded"]
    
    # Extract product name (for folder name)
    name_graph = SmartScraperGraph(
        prompt="Extract only the product name/title as plain text.",
        source=product_url,
        config={"llm": llm_config},
    )
    name_result = name_graph.run()
    product_name = name_result.get('content', f"product_{product_index}")
    
    # Clean product name for folder usage
    safe_name = sanitize_filename(product_name)
    product_folder = os.path.join(base_output_dir, safe_name)
    
    print(f"Product name: {product_name}")
    
    # Extract product images
    image_graph = SmartScraperGraph(
        prompt="Extract all product image URLs from this page. Return as a JSON array.",
        source=product_url,
        config={"llm": llm_config},
    )
    image_result = image_graph.run()
    image_urls = image_result.get('content', [])
    
    # Update report counts
    report_data["total_images_found"] += len(image_urls)
    
    # Download images
    print(f"Found {len(image_urls)} images")
    downloaded_count = 0
    for j, img_url in enumerate(image_urls):
        # Try to get extension from URL, default to jpg
        try:
            ext = img_url.split('?')[0].split('.')[-1] 
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'
        except:
            ext = 'jpg'
            
        if download_image(img_url, product_folder, f"image_{j+1}.{ext}", min_size=(min_size, min_size)):
            downloaded_count += 1
    
    print(f"Downloaded {downloaded_count} images (skipped {len(image_urls) - downloaded_count} due to size or errors)")
    
    # Add to product data
    product_data = {
        "name": product_name,
        "url": product_url,
        "images_found": len(image_urls),
        "images_downloaded": downloaded_count,
        "skipped": False
    }
    
    # Add to category products list
    category_data["products"].append(product_data)
    
    # Update counters
    category_data["products_processed"] += 1
    category_data["images_downloaded"] += downloaded_count
    
    # Save to processed products
    processed_data["processed_products"][product_url] = {
        "name": product_name,
        "images_found": len(image_urls),
        "images_downloaded": downloaded_count,
        "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return product_name, downloaded_count

def process_category_page(category_url, category_index, output_dir, processed_data, min_size=301):
    """Process a category page to extract all product URLs, then process each product"""
    print(f"\n{'='*80}")
    print(f"CATEGORY {category_index}: {category_url}")
    print(f"{'='*80}")
    
    # Check if category was already processed
    if category_url in processed_data["processed_categories"]:
        category_info = processed_data["processed_categories"][category_url]
        print(f"Category already processed: {category_info['name']} ({category_info['processed_date']})")
        print(f"Use --force to reprocess or remove entry from {PROCESSED_LOG_FILE}")
        
        # Create a placeholder category entry for the report
        category_data = {
            "name": category_info["name"],
            "url": category_url,
            "products_processed": category_info["products_processed"],
            "images_downloaded": category_info["images_downloaded"],
            "products": [],
            "skipped": True
        }
        report_data["categories"].append(category_data)
        report_data["total_products"] += category_info["products_processed"]
        report_data["total_images_downloaded"] += category_info["images_downloaded"]
        
        return category_info["products_processed"]
    
    # Create category folder using the category name from URL
    category_name = extract_category_name(category_url)
    category_folder = os.path.join(output_dir, category_name)
    os.makedirs(category_folder, exist_ok=True)
    
    print(f"Using category name from URL: {category_name}")
    
    # Initialize category data for the report
    category_data = {
        "name": category_name,
        "url": category_url,
        "products_processed": 0,
        "images_downloaded": 0,
        "products": [],
        "skipped": False
    }
    report_data["categories"].append(category_data)
    
    # Extract product URLs from category page
    category_graph = SmartScraperGraph(
        prompt="Extract all product URLs from this category/listing page. Return as a JSON array of strings.",
        source=category_url,
        config={"llm": llm_config},
    )
    product_urls_result = category_graph.run()
    
    # Handle different response formats
    if isinstance(product_urls_result, dict) and 'content' in product_urls_result:
        product_urls = product_urls_result['content']
    elif isinstance(product_urls_result, list):
        product_urls = product_urls_result
    else:
        print(f"Error: Unexpected response format: {type(product_urls_result)}")
        print(f"Response: {product_urls_result}")
        return 0
    
    # Ensure product_urls is a list
    if not isinstance(product_urls, list):
        if isinstance(product_urls, str):
            # Try to handle case where it's a single URL as string
            product_urls = [product_urls]
        else:
            print(f"Error: Expected a list of product URLs, got {type(product_urls)}")
            return 0
    
    # Filter product URLs to only include those from the current category
    print(f"Found {len(product_urls)} URLs before filtering")
    filtered_product_urls = filter_product_urls(product_urls, category_url)
    print(f"Found {len(filtered_product_urls)} product URLs after filtering (belonging to this category)")
    
    if len(filtered_product_urls) == 0:
        print("No product URLs found for this category. Check if the site structure is as expected.")
        print("You might need to adjust the filtering logic or the prompt for extracting product URLs.")
        return 0
    
    # Process each product URL
    products_processed = 0
    for i, url in enumerate(filtered_product_urls):
        try:
            product_name, image_count = process_product_page(url, i+1, category_folder, category_data, processed_data, min_size)
            products_processed += 1
            report_data["total_products"] += 1
            
            # Rate limiting between products
            if i < len(filtered_product_urls) - 1:
                time.sleep(1)  # 1 second between product pages
                
        except Exception as e:
            print(f"Error processing product {i+1}: {e}")
    
    # Save category to processed data
    processed_data["processed_categories"][category_url] = {
        "name": category_name,
        "products_processed": category_data["products_processed"],
        "images_downloaded": category_data["images_downloaded"],
        "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return products_processed

def main():
    """Main function to run the scraper"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Multi-level web scraper for product images')
    parser.add_argument('--force', action='store_true', help='Force reprocessing of already processed items')
    parser.add_argument('--min-size', type=int, default=301, help='Minimum image size (both width and height)')
    args = parser.parse_args()
    
    # Create output directory
    output_dir = "scraped_products"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create/check category URLs file
    if not create_category_urls_file():
        return
    
    # Read category URLs from file
    try:
        with open('category_urls.txt', 'r') as f:
            category_urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        print(f"Error reading category_urls.txt: {e}")
        return
    
    if not category_urls:
        print("No category URLs found in category_urls.txt. Please add URLs and run again.")
        return
    
    print(f"Found {len(category_urls)} category URLs to process.")
    print(f"Using minimum image size: {args.min_size}x{args.min_size} pixels")
    
    # Load processed items
    processed_data = load_processed_items()
    
    # If force option is used, clear processed items
    if args.force:
        print("Force option used - will reprocess all items")
        processed_data = {
            "processed_categories": {},
            "processed_products": {}
        }
    
    # Initialize report data
    global report_data
    report_data = {
        "timestamp": "",
        "categories": [],
        "total_products": 0,
        "total_images_found": 0,
        "total_images_downloaded": 0,
        "total_images_skipped": 0,
        "failed_urls": []
    }
    
    # Process each category
    total_categories = len(category_urls)
    total_products = 0
    
    for i, url in enumerate(category_urls):
        products_count = process_category_page(url, i+1, output_dir, processed_data, args.min_size)
        total_products += products_count
        
        # Save processed items after each category
        save_processed_items(processed_data)
        
        # Rate limiting between categories
        if i < total_categories - 1:
            time.sleep(2)  # 2 seconds between category pages
    
    # Generate report
    generate_report()
    
    print(f"\n{'='*80}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*80}")
    print(f"Processed {total_categories} categories")
    print(f"Processed {total_products} products")
    print(f"Found {report_data['total_images_found']} images")
    print(f"Downloaded {report_data['total_images_downloaded']} images")
    print(f"Skipped {report_data['total_images_skipped']} images")
    print(f"Results saved to {os.path.abspath(output_dir)}")
    print(f"Report generated: {os.path.abspath(REPORT_FILE)}")
    print(f"Processed items log: {os.path.abspath(PROCESSED_LOG_FILE)}")

if __name__ == "__main__":
    main() 