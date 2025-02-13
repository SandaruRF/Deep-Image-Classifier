from playwright.sync_api import sync_playwright
import os
import requests
from io import BytesIO
from PIL import Image

def download_image(url, folder, index):
    try:
        print(url)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            width, height = image.size
            if (("image/jpeg" in response.headers.get("Content-Type", "")) and (width>100 and height>100)):
                file_extension = ".jpg"
                filename = os.path.join(folder, f"{folder}_image_{index}{file_extension}")
                with open(filename, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded: {filename}")
                return (index + 1)
            return index
        else:
            print(f"Failed to download {url}")
            return index
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return index

def scrape_google_images(query, max_images):
    folder = query.replace(" ", "_")
    os.makedirs(folder, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)  # Set headless=True if you don't want a visible browser
        page = browser.new_page()
        
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"
        page.goto(search_url)

        image_links = set()  # Use a set to avoid duplicates

        while len(image_links) < max_images:
            print(len(image_links))
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)  # Wait 2 seconds for new images to load

            # Extract all images
            images = page.locator("xpath=//img").all()

            for image in images:
                src = image.get_attribute("src")
                if src:
                    image_links.add(src)
                
                if len(image_links) >= max_images:
                    break

        print(f"Total Images Found: {len(image_links)}")

        downloaded_images = 0
        for index, link in enumerate(image_links):
            if (downloaded_images>=int(max_images/5)):
                break
            if (link.startswith("http")):
                downloaded_images = download_image(link, query, downloaded_images)

        browser.close()
        return image_links

number_of_images = 50
search_prompt = "cat"
image_urls = scrape_google_images(search_prompt, number_of_images*5)
