# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="/Users/sydney/.wdm/drivers/chromedriver/mac64/87.0.4280.88/chromedriver", headless=True)
   
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None 

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url


def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # Assign columns and set index to dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


def mars_hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # parse HTML with BeautifulSoup
    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')

    # base URL
    base_url ="https://astrogeology.usgs.gov"

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    hemisphere_infos = hemisphere_soup.find_all('div', class_='item')

    for info in hemisphere_infos:
        hemispheres = {}
        
        img_url_rel = info.find('a', class_='itemLink product-item').get("href")
        img_url = base_url + img_url_rel
        browser.visit(img_url)
        
        # parse HTML with BeautifulSoup
        html = browser.html
        hemispheres_image_soup = soup(html, 'html.parser')
        
        # retrieve full image 
        full_img_url = hemispheres_image_soup.find('div', class_='downloads').find('a').get('href')
        
        # retrieve image title
        img_title = hemispheres_image_soup.find('h2', class_='title').text
        
        # Append information to a dictionary
        hemisphere_image_urls.append({"img_url" : full_img_url, "title" : img_title})
    
    return hemisphere_image_urls



if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())