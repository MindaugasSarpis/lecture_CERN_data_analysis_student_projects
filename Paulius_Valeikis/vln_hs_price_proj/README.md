# house_listing_scraper
repeatedly scrape aruodas for house prices for use in data analysis projects


1. nusiklonuok github repo

2. reikia poetry(reiksia veiks tik linux ir macos, arba wsl)
poetry install

3. naudojimas(nueik i kur nukolnuotas repo)
# paleisti pipline
poetry run aruodas run

# gauti surinktus runus

poetry run aruodas export

# jei reikia tik paskutinio

poetry run aruodas export --latest


