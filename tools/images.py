import time

# City-specific curated image URLs
CITY_IMAGES = {
    "paris": [
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80",
        "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&q=80",
        "https://images.unsplash.com/photo-1431274172761-fcdab704a698?w=800&q=80",
    ],
    "tokyo": [
        "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
        "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=800&q=80",
        "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?w=800&q=80",
    ],
    "new york": [
        "https://images.unsplash.com/photo-1518235506717-e1ed3306a89b?w=800&q=80",
        "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800&q=80",
        "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=800&q=80",
    ],
    "kyoto": [
        "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
        "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80",
        "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80",
    ],
    "dubai": [
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80",
        "https://images.unsplash.com/photo-1518684079-3c830dcef090?w=800&q=80",
        "https://images.unsplash.com/photo-1526495124232-a04e1849168c?w=800&q=80",
    ],
    "london": [
        "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80",
        "https://images.unsplash.com/photo-1529655683826-aba9b3e77383?w=800&q=80",
        "https://images.unsplash.com/photo-1520986606214-8b456906c813?w=800&q=80",
    ],
    "sydney": [
        "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=800&q=80",
        "https://images.unsplash.com/photo-1524820801657-fd59673fbb05?w=800&q=80",
        "https://images.unsplash.com/photo-1530276371169-2f78f7b8a6f1?w=800&q=80",
    ],
    "new delhi": [
        "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80",
        "https://images.unsplash.com/photo-1597040663342-45b6af3d91a5?w=800&q=80",
        "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&q=80",
    ],
    "mumbai": [
        "https://images.unsplash.com/photo-1595658658481-d53d3f999875?w=800&q=80",
        "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?w=800&q=80",
        "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&q=80",
    ],
    "rome": [
        "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&q=80",
        "https://images.unsplash.com/photo-1555992336-03a23c7b20ee?w=800&q=80",
        "https://images.unsplash.com/photo-1529260830199-42c24126f198?w=800&q=80",
    ],
    "barcelona": [
        "https://images.unsplash.com/photo-1523531294919-4bcd7c65e216?w=800&q=80",
        "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=800&q=80",
        "https://images.unsplash.com/photo-1464790719320-516ecd75af6c?w=800&q=80",
    ],
    "singapore": [
        "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&q=80",
        "https://images.unsplash.com/photo-1508964942454-1a56651d54ac?w=800&q=80",
        "https://images.unsplash.com/photo-1565967511849-76a60a516170?w=800&q=80",
    ],
    "amsterdam": [
        "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800&q=80",
        "https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?w=800&q=80",
        "https://images.unsplash.com/photo-1583064313642-a7c149480c7e?w=800&q=80",
    ],
    "bangkok": [
        "https://images.unsplash.com/photo-1563492065599-3520f775eeed?w=800&q=80",
        "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800&q=80",
        "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&q=80",
    ],
    "snohomish": [
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80",
        "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&q=80",
    ],
    "japan": [
        "https://images.unsplash.com/photo-1526481280693-3bfa7568e0f3?w=800&q=80",
        "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80",
        "https://images.unsplash.com/photo-1480796927426-f609979314bd?w=800&q=80",
    ],
    "cairo": [
        "https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=800&q=80",
        "https://images.unsplash.com/photo-1539650116574-75c0e2973f6d?w=800&q=80",
        "https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=800&q=80",
    ],
    "istanbul": [
        "https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=800&q=80",
        "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800&q=80",
        "https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800&q=80",
    ],
    "toronto": [
        "https://images.unsplash.com/photo-1517090504586-fde19ea6066f?w=800&q=80",
        "https://images.unsplash.com/photo-1507992781348-310259076fe0?w=800&q=80",
        "https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=800&q=80",
    ],
    "moscow": [
        "https://images.unsplash.com/photo-1513326738677-b964603b136d?w=800&q=80",
        "https://images.unsplash.com/photo-1596484552834-6a58f850e0a1?w=800&q=80",
        "https://images.unsplash.com/photo-1547448415-e9f5b28e570d?w=800&q=80",
    ],
}

# Generic travel fallbacks — varied so different unknown cities
# get different images based on first letter of city name
GENERIC_POOLS = [
    [
        "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&q=80",
        "https://images.unsplash.com/photo-1488085061387-422e29b40080?w=800&q=80",
        "https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=800&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1500835556837-99ac94a94552?w=800&q=80",
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80",
        "https://images.unsplash.com/photo-1507608616759-54f48f0af0ee?w=800&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1452421822248-d4c2b47f0c81?w=800&q=80",
        "https://images.unsplash.com/photo-1501554728187-ce583db33af7?w=800&q=80",
        "https://images.unsplash.com/photo-1528543606781-2f6e8759f1b7?w=800&q=80",
    ],
    [
        "https://images.unsplash.com/photo-1473625247510-8ceb1760943f?w=800&q=80",
        "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=800&q=80",
        "https://images.unsplash.com/photo-1504512485720-7d83a16ee930?w=800&q=80",
    ],
]


def get_city_images(city: str) -> list:
    """
    Returns image URLs specific to the city.
    Known cities → curated photos.
    Unknown cities → unique generic pool based on city name hash,
                     so different cities get different images.
    """
    time.sleep(0.6)
    city_lower = city.lower().strip()

    if city_lower in CITY_IMAGES:
        return CITY_IMAGES[city_lower]

    # Pick a unique pool based on city name so each unknown
    # city gets different images (not the same default every time)
    pool_index = sum(ord(c) for c in city_lower) % len(GENERIC_POOLS)
    return GENERIC_POOLS[pool_index]