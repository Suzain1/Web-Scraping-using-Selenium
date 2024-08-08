🛒 Web Scraping Product Reviews with Selenium
This repository contains a Python script that automates the process of scraping product reviews from e-commerce websites, specifically Amazon. The script uses Selenium to search for products by serial number, navigate to the product page, and extract reviews and other relevant information.

📋 Features
Automated Web Scraping: The script automates the process of searching for products and extracting data using Selenium.
Data Processing: After scraping, the data is cleaned and processed for further analysis.
Browser Automation: Uses WebDriverManager to handle browser drivers efficiently.
Error Handling: Includes basic error handling to manage unavailable products or missing data.

🛠️ Requirements
Python 3.x
Selenium
Pandas
WebDriverManager

📝 Script Overview
setup_driver: Initializes the Selenium WebDriver and sets up wait conditions.
search_product: Searches for the product on Google and navigates to the Amazon page.
check_name: Verifies the product name against the serial number.
scrape_reviews: Extracts the product reviews from the page.
