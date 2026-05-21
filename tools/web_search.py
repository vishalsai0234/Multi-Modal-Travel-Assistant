import time

# Mock search results for cities not in the vector store
MOCK_SEARCH_DB = {
    "kyoto": """Kyoto is a city on the island of Honshu in Japan. It served as Japan's capital and the emperor's residence 
    from 794 until 1869. Known as the 'City of Ten Thousand Shrines', Kyoto is home to numerous Buddhist temples, 
    Shinto shrines, palaces, and traditional wooden machiya townhouses. The city is famous for its geisha culture, 
    centered in districts like Gion and Pontocho. Fushimi Inari Taisha, with its thousands of vermillion torii gates, 
    is one of Japan's most visited shrines. The Arashiyama Bamboo Grove is one of Kyoto's most photographed spots. 
    Kinkaku-ji (the Golden Pavilion) is a Zen temple whose top two floors are completely covered in gold leaf. 
    Kyoto has 17 UNESCO World Heritage Sites. The city is known for its seasonal beauty — cherry blossoms in spring 
    and vivid maple foliage in autumn. Traditional arts like tea ceremony, ikebana (flower arranging), and Noh theater 
    remain active in the city.""",

    "snohomish": """Snohomish is a small city in Snohomish County in the state of Washington, United States. 
    Located about 30 miles northeast of Seattle, it sits along the Snohomish River. The city is known for its 
    well-preserved Victorian-era downtown, antique shops, and historic First Street. Snohomish is often called 
    the 'Antique Capital of the Northwest'. The city has a small-town charm with a population of around 10,000 people. 
    It is near the Cascade Mountains, offering access to outdoor activities. The Harvey Airfield near Snohomish is 
    one of the most active general aviation airports in Washington State. The Pilchuck Glass School, an internationally 
    renowned art school, is located in the nearby area. Snohomish is a starting point for exploring the scenic 
    Cascade Loop Highway.""",

    "dubai": """Dubai is the largest and most populous city in the United Arab Emirates (UAE). 
    Known for its ultramodern architecture and luxury lifestyle, Dubai has transformed from a small fishing village 
    into a global metropolis in just a few decades. The Burj Khalifa, standing at 828 meters, is the world's tallest 
    building and a defining symbol of the city. The Dubai Mall is one of the world's largest shopping centers. 
    Palm Jumeirah is an artificial archipelago created from reclaimed land and is home to luxury hotels and residences. 
    Dubai has one of the busiest airports in the world, Dubai International Airport, serving over 80 million passengers 
    annually. The city is a major hub for finance, tourism, aviation, real estate, and international trade. 
    The Dubai Frame, a giant picture frame-shaped skyscraper, offers views of both old and new Dubai. 
    The traditional Deira Gold Souk and Spice Souk offer a glimpse into the city's trading heritage.""",
}

GENERIC_TEMPLATE = """{city} is a fascinating destination that attracts visitors from around the world. 
The city offers a unique blend of culture, history, and modern attractions. Travelers can explore 
local markets, historical sites, and experience the authentic local cuisine. The city is known for 
its warm hospitality and vibrant community. Whether you are interested in architecture, food, art, 
or outdoor activities, {city} has something to offer every type of traveler. The local transportation 
system makes it easy to navigate between attractions, and there are accommodations available for 
every budget from hostels to luxury hotels."""


def mock_web_search(city: str) -> str:
    """
    Simulates a web search for cities not in the local vector store.
    Returns structured text information about the city.
    """
    time.sleep(1.5)  # web search takes longer than local DB
    city_lower = city.lower()

    if city_lower in MOCK_SEARCH_DB:
        return MOCK_SEARCH_DB[city_lower]

    # Generic fallback for completely unknown cities
    return GENERIC_TEMPLATE.format(city=city)
