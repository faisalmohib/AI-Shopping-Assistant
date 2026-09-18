

import requests
import sqlite3
import time
from datetime import datetime

# =========================
# CONFIG
# =========================

BASE_URL = "https://www.junaidjamshed.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Run every 2 hours
SCRAPE_INTERVAL = 2 * 60 * 60

# =========================
# WOMEN COLLECTIONS
# =========================

COLLECTIONS = [
    "https://www.junaidjamshed.com/collections/womens-stitched",
    "https://www.junaidjamshed.com/collections/womens-un-stitched",
    "https://www.junaidjamshed.com/collections/womens-formals",
    "https://www.junaidjamshed.com/collections/womens-footwear",
    "https://www.junaidjamshed.com/collections/womens-accessories",
    "https://www.junaidjamshed.com/collections/fragrances-for-women",
    "https://www.junaidjamshed.com/collections/makeup",
    "https://www.junaidjamshed.com/collections/skin-care"
]

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("products.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS PRODUCTS(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER UNIQUE,
    name TEXT,
    price REAL,
    color TEXT,
    brand TEXT,
    image TEXT,
    url TEXT UNIQUE,
    target_audience TEXT,
    category TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS PRODUCT_VARIANTS(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    size TEXT,
    available INTEGER,
    UNIQUE(product_id, size)
)
""")

conn.commit()

# =========================
# HELPERS
# =========================

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def get_json(url, retries=3):
    """
    Download JSON with retry.
    """

    for attempt in range(retries):

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=20
            )

            if response.status_code == 200:
                return response.json()

            log(f"HTTP {response.status_code} -> {url}")

        except Exception as e:
            log(f"Attempt {attempt+1}: {e}")

        time.sleep(2)

    return None


def get_products(collection_url):

    data = get_json(
        collection_url + "/products.json?limit=250"
    )

    if data:
        return data.get("products", [])

    return []


def get_audience(url):
    return "Women"


def get_category(url):

    url = url.lower()

    if "womens-stitched" in url:
        return "women_stitched"

    elif "womens-un-stitched" in url:
        return "women_unstitched"

    elif "womens-formals" in url:
        return "women_formals"

    elif "womens-footwear" in url:
        return "women_footwear"

    elif "womens-accessories" in url:
        return "women_accessories"

    elif "fragrances-for-women" in url:
        return "women_fragrances"

    elif "makeup" in url:
        return "women_makeup"

    elif "skin-care" in url:
        return "women_skin_care"

    return "general"


# =========================
# DATABASE FUNCTIONS
# =========================

def insert_product(data):

    cursor.execute("""
    INSERT INTO PRODUCTS
    (
        product_id,
        name,
        price,
        color,
        brand,
        image,
        url,
        target_audience,
        category
    )

    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?)

    ON CONFLICT(product_id)

    DO UPDATE SET

        name=excluded.name,
        price=excluded.price,
        color=excluded.color,
        brand=excluded.brand,
        image=excluded.image,
        url=excluded.url,
        target_audience=excluded.target_audience,
        category=excluded.category

    """, data)

    conn.commit()


def insert_variant(data):

    cursor.execute("""
    INSERT INTO PRODUCT_VARIANTS
    (
        product_id,
        size,
        available
    )

    VALUES
    (?, ?, ?)

    ON CONFLICT(product_id,size)

    DO UPDATE SET

        available=excluded.available

    """, data)

    conn.commit()


# =========================
# SCRAPER FUNCTION
# =========================

def run_scraper():

    total_products = 0
    total_variants = 0

    log("Starting scraper...")

    for col in COLLECTIONS:

        log("=" * 60)
        log(f"Collection: {col}")

        audience = get_audience(col)
        category = get_category(col)

        products = get_products(col)

        log(f"Found {len(products)} products")

        for p in products:

            try:

                product_id = p.get("id")
                name = p.get("title")
                brand = "J."

                url = BASE_URL + "/products/" + p.get("handle")

                image = None
                images = p.get("images", [])

                if images:
                    image = images[0].get("src")

                variants = p.get("variants", [])

                price = 0
                color = None

                if variants:
                    try:
                        price = float(variants[0].get("price", 0))
                    except:
                        price = 0

                    for opt in [
                        variants[0].get("option1"),
                        variants[0].get("option2"),
                        variants[0].get("option3")
                    ]:
                        if (
                            opt
                            and str(opt).upper() not in [
                                "XS", "S", "M", "L",
                                "XL", "XXL", "XXXL",
                                "FREE", "N/A"
                            ]
                        ):
                            color = opt
                            break

                insert_product((
                    product_id,
                    name,
                    price,
                    color,
                    brand,
                    image,
                    url,
                    audience,
                    category
                ))

                total_products += 1

                for v in variants:

                    size = (
                        v.get("option1")
                        or v.get("option2")
                        or "N/A"
                    )

                    available = 1 if v.get("available") else 0

                    insert_variant((
                        product_id,
                        size,
                        available
                    ))

                    total_variants += 1

                log(f"Saved: {name}")

                time.sleep(0.1)

            except Exception as e:
                log(f"Error while processing product: {e}")

    log("=" * 60)
    log("SCRAPING COMPLETED")
    log(f"Products Processed : {total_products}")
    log(f"Variants Processed : {total_variants}")
    log("=" * 60)

# ===================================================
# MAIN LOOP
# ===================================================

if __name__ == "__main__":

    log("Automatic Scraper Started")

    try:

        while True:

            start = time.time()

            try:
                run_scraper()

            except Exception as e:
                log(f"Scraper crashed: {e}")

            elapsed = int(time.time() - start)

            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60

            log(
                f"Run completed in "
                f"{hours}h {minutes}m {seconds}s"
            )

            log("Waiting 2 hours for next execution...")
            log("=" * 60)

            time.sleep(SCRAPE_INTERVAL)

    except KeyboardInterrupt:

        log("Scraper stopped by user.")

    finally:

        conn.close()
        log("Database connection closed.")