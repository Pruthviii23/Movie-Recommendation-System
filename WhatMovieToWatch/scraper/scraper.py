import time
import random
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ---------------- CONFIG ---------------- #

SEARCH_URL = (
    "https://www.imdb.com/search/title/"
    "?title_type=feature"
    "&release_date=2000-01-01,2025-12-31"
    "&num_votes=1000,"
    "&countries=IN"
    "&sort=year,desc"
)

OUTPUT_FILE = "indian_movies_2000_2025.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

MAX_MOVIES = 4700        # safety cap
CAST_LIMIT = 5           # top N cast


# ---------------- UTILS ---------------- #

def safe_request(url, retries=3):
    for _ in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r
        except:
            time.sleep(2)
    return None


def scrape_movie_page(movie_url):
    r = safe_request(movie_url)
    if not r:
        return None, None, None

    soup = BeautifulSoup(r.text, "html.parser")

    # Tags / Genres (interest chips)
    tags = []
    chip_container = soup.select_one("div.ipc-chip-list__scroller")
    if chip_container:
        for chip in chip_container.select("span.ipc-chip__text"):
            tags.append(chip.text.strip())
    tags = ", ".join(tags) if tags else None

    # Director (first name credit)
    director = None
    director_tag = soup.select_one('a[href^="/name/"]')
    if director_tag:
        director = director_tag.text.strip()

    # Cast
    cast = []
    for actor in soup.select('a[data-testid="title-cast-item__actor"]')[:CAST_LIMIT]:
        cast.append(actor.text.strip())
    cast = ", ".join(cast) if cast else None

    return tags, director, cast


# ---------------- MAIN SCRAPER ---------------- #

def main():
    # ---- Resume handling ----
    if os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0:
        df = pd.read_csv(OUTPUT_FILE)
        scraped_ids = set(df["movie_id"])
        print(f"🔁 Resuming – {len(scraped_ids)} movies already scraped")
    else:
        df = pd.DataFrame(columns=[
            "movie_id", "movie_name", "year",
            "tags", "overview", "rating",
            "director", "cast"
        ])
        scraped_ids = set()
        print("🆕 Starting fresh scrape")

    # ---- Selenium setup ----
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 20)
    driver.get(SEARCH_URL)

    time.sleep(3)

    # ---- Load all movies by clicking "50 more" ----
    print("📜 Loading all movies…")

    last_count = 0
    while True:
        movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
        current_count = len(movies)

        print(f"Loaded movies: {current_count}")

        if current_count >= MAX_MOVIES or current_count == last_count:
            break

        last_count = current_count

        try:
            btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.ipc-see-more__button")
                )
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(random.uniform(2.5, 4))
        except:
            break

    print(f"✅ Total movies loaded in DOM: {len(driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item'))}")

    # ---- Scrape movies ----
    movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")

    new_rows = []

    for item in tqdm(movies, desc="🎬 Scraping movies"):
        try:
            title_el = item.find_element(By.CSS_SELECTOR, "h3.ipc-title__text")
            movie_name = title_el.text.split(". ", 1)[-1]

            link_el = item.find_element(By.CSS_SELECTOR, "a.ipc-title-link-wrapper")
            href = link_el.get_attribute("href")
            movie_id = href.split("/")[4]
            movie_url = href.split("?")[0]

            if movie_id in scraped_ids:
                continue

            year = item.find_element(By.CSS_SELECTOR, "span.dli-title-metadata-item").text
            rating = item.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--rating").text
            overview = item.find_element(By.CSS_SELECTOR, ".title-description-plot-container").text.strip()

            tags, director, cast = scrape_movie_page(movie_url)

            new_rows.append({
                "movie_id": movie_id,
                "movie_name": movie_name,
                "year": year,
                "tags": tags,
                "overview": overview,
                "rating": rating,
                "director": director,
                "cast": cast
            })

            scraped_ids.add(movie_id)

            # incremental save every 25 movies
            if len(new_rows) >= 25:
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                df.to_csv(OUTPUT_FILE, index=False)
                new_rows.clear()

            time.sleep(random.uniform(1.2, 2.0))

        except Exception as e:
            continue

    # final save
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(OUTPUT_FILE, index=False)

    driver.quit()
    print(f"\n✅ SCRAPING COMPLETE")
    print(f"📁 Saved to {OUTPUT_FILE}")
    print(f"🎥 Total movies scraped: {len(df)}")


if __name__ == "__main__":
    main()