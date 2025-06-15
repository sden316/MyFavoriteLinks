def read_file(file_path):
    """
    Read and return the contents of a text file.
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: Contents of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

def is_valid_url(url):
    """
    Check if a URL is valid by making a HEAD request.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    import requests
    from urllib3.exceptions import InsecureRequestWarning
    import requests.exceptions
    
    # Suppress only the InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    try:
        response = requests.head(url, allow_redirects=True, timeout=5, verify=False)
        return response.status_code < 400
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False

def extract_links(content):
    """
    Extract all URLs from the given text content.
    
    Args:
        content (str): Text content to extract links from
        
    Returns:
        list: List of URLs found in the content
    """
    import re
    
    # Pattern to match URLs
    url_pattern = r'https?://[^\s<>\[\]\"\']+|www\.[^\s<>\[\]\"\']+\.[^\s<>\[\]\"\']+'
    
    if not content:
        return []
    
    # Find all matches and return as list
    links = re.findall(url_pattern, content)
    return links

def save_links_by_domain(links):
    """
    Save valid links to separate files based on their domain.
    
    Args:
        links (list): List of URLs to categorize and save
    """
    import os
    from urllib.parse import urlparse
    from concurrent.futures import ThreadPoolExecutor
    from tqdm import tqdm

    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Dictionary to store links by domain
    domain_links = {
        "facebook": [],
        "linkedin": [],
        "youtube": [],
        "other": []
    }

    # Validate and categorize links using ThreadPoolExecutor
    valid_links = []
    print("\nValidating links... (this may take a few minutes)")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create a list of futures for validation tasks
        futures = {executor.submit(is_valid_url, link): link for link in links}
        
        # Process results as they complete with a progress bar
        for future in tqdm(futures, total=len(links), desc="Validating"):
            link = futures[future]
            try:
                if future.result():
                    valid_links.append(link)
            except Exception as e:
                print(f"Error validating {link}: {str(e)}")

    # Categorize valid links by domain
    for link in valid_links:
        parsed_url = urlparse(link)
        domain = parsed_url.netloc.lower()
        
        if "facebook.com" in domain:
            domain_links["facebook"].append(link)
        elif "linkedin.com" in domain:
            domain_links["linkedin"].append(link)
        elif "youtube.com" in domain or "youtu.be" in domain:
            domain_links["youtube"].append(link)
        else:
            domain_links["other"].append(link)

    total_valid = len(valid_links)
    total_invalid = len(links) - total_valid
    print(f"\nValidation complete:")
    print(f"Total links: {len(links)}")
    print(f"Valid links: {total_valid}")
    print(f"Invalid links: {total_invalid}")

    # Save valid links to separate files
    for domain, domain_specific_links in domain_links.items():
        if domain_specific_links:  # Only create file if there are links
            file_path = os.path.join(output_dir, f"{domain}_links.txt")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for link in domain_specific_links:
                        f.write(f"{link}\n")
                print(f"Saved {len(domain_specific_links)} valid {domain} links to {file_path}")
            except IOError as e:
                print(f"Error saving {domain} links: {e}")

def main():
    print("Hello from documentation!")
    # Example usage of read_file
    content = read_file("input/_chat.txt")
    if content:
        print("\nExtracting links from chat...")
        links = extract_links(content)
        print(f"\nFound {len(links)} links")
        
        print("\nSaving valid links by domain...")
        save_links_by_domain(links)

if __name__ == "__main__":
    main()
