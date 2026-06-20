#Creates an art gallery scraper that gatehrs image urls for a database
# imports
# If these fail, please check you're running from an 'activated' environment with (llms) in the command prompt

import os
import json
from dotenv import load_dotenv
from IPython.display import Markdown, display, update_display
from scraper import fetch_website_links, fetch_website_contents
from openai import OpenAI
# Initialize and constants
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL_NAME="llama3.2"

ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')
links = fetch_website_links("https://texashistory.unt.edu/explore/collections/t/")
links
link_system_prompt = """

You are provided with a webpage that hosts images of many different types of art. You should focus specficially on paintings but it does not matter what medium 
You have the ability to click on different links within the webpage and find the urls to different paintings that are given to you by the user. This is for a database.
You should respond in JSON as in this example:
CRITICAL: You must copy the URLs EXACTLY as they appear in the user prompt. Y as they appear in the user prompt. Do not truncate, change numbers, shorten hashes, or modify the string paths in any way.

{
    "links": [
        {"type": "name of artwork 1", "url": "https://full.url/url-of-a-painting"},
        {"type": "name of artwork 2", "url": "https://another.full.url/url-of-a-painting"}
    ]
}

If you cannot find the image url for an artwork, just return "NONE" in the url
"""
def get_links_user_prompt(url):

    artists_lists = ['William Prickett', 'William Ort', 'William Nies', 'William Neusser', 'William Morris', 'William Maher', 'William Loose', 'William Lester', 'William Ledward', 'William Kleine', 'William Keiller', 'William Huddle', 'William Houliston', 'William Higgins', 'William Henry', 'William Fausett', 'William Elliott', 'William Cole', 'William Casey', 'William Cannings', 'William Buck', 'William Bryant', 'William Bryan', 'William Besser', 'William Baker', 'William Addis', 'Willet Oaul', 'Will Richter', 'Will Henry', 'Wilfred Stedman', 'Wiley Fuqua', 'Wildman Morrill', 'Wilburn Tee', 'Wilburine Dudley', 'Wickes Aline', 'White Victoria', 'White Rena', 'White Pearl', 'White Mrs', 'White Marie', 'White Lula', 'White Lena', 'White Harper', 'White Florence', 'White Aline', 'Wheeler Maud', 'Wheeler Demark', 'West Ethel', 'West Artists', 'Werner Dumuth', 'Welmaker Fred', 'Wellington Cornell', 'Weisser Fred', 'Weisser Beulah', 'Weisner Orth', 'Weise Paul', 'Weisberg Marie', 'Weisberg Joe', 'Webster Mary', 'Webb Frank', 'Webb Esther', 'Watts Green', 'Watson Neyland', 'Watson Joe', 'Watkins Sam', 'Warren Phelps', 'Warren Hunter', 'Warren Hohnstedt', 'Warren Helen', 'Warner William', 'Warlick Mildred', 'Ward Lockwood', 'Wanda Hermann', 'Walton Spigener', 'Walton Leader', 'Walter Stockwell', 'Walter Stevens', 'Walter Rolfe', 'Walter Merrill', 'Walter Kuttner', 'Walter King', 'Walter Hosek', 'Walter Herrington', 'Walter Haggart', 'Walter Gresham', 'Walmsley Elizabeth', 'Waller Virginia', 'Waller Mary', 'Wallace Wells', 'Wallace Simpson', 'Walker Tecla', 'Walker Phil', 'Walker Jack', 'Waldine Tauch', 'Waide Clara', 'Wagner', 'Waggoner Harry', 'Waggener ☑', 'Wade Ted', 'Wade Jolly', 'W.e. Swearingen']
    raw_scraped_links = fetch_website_links(url)
    filtered_links = []
    base_url = "https://www.artic.edu/"
    for link in raw_scraped_links:
        if any(ignore in link for ignore in ["/about","/contact","/css","/js","javascript:"]):
            continue
        if link.startswith("/"):
            absolute_link = urljoin(base_url, link)
        else:
            absolute_link = link 
# NEW PYTHON FILTER: Convert link to lowercase to check against our artists
        link_lower = absolute_link.lower()
        
        # Only keep the link if it actually matches one of our target artists
        matches_artist = False
        for artist in artists_lists:
            # Clean up names (e.g., "William Lester" -> "william" and "lester") to match URL slugs
            name_parts = artist.lower().split()
            if len(name_parts) >= 2 and (name_parts[0] in link_lower or name_parts[1] in link_lower):
                matches_artist = True
                break
                
        if matches_artist:
            filtered_links.append(absolute_link)
    user_prompt = f"""
Analyze the links scraped from {url}
Match them with target artists from the roster: {", ".join(artists_lists)}
Extract the valdi artwork item paths and format them into the requested JSON schema.
Links:


"""
    user_prompt += "\n".join(filtered_links)
    return user_prompt
print(get_links_user_prompt("https://www.artic.edu/collection?q=paintings"))
def select_relevant_links(url):
    response = ollama.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    result_text = response.choices[0].message.content
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        print("Model failed to return clean JSON object. Raw response:")
        print(result_text)
        return{"links":[]}
    

target_collection_url = "https://www.artic.edu/collection?q=paintings"
found_art_data = select_relevant_links(target_collection_url)
print(json.dumps(found_art_data, indent=4))