import aiohttp
import asyncio

from bs4 import BeautifulSoup as soup
import datetime
import pickle

#Fetch function (this is the one that can take a while, so I raise an error if it takes too long)
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

#Main loop
async def main():
	first_week = '1958-08-04'
	date_obj = datetime.datetime.strptime(first_week, '%Y-%m-%d').date()

	url = 'https://www.billboard.com/charts/hot-100/' + first_week
	data = []

	fname = 'Songs'

	timeouts = 0
	date_changes = 0

	#timeout object
	timeout = aiohttp.ClientTimeout(total = 10)

	#While date is less than current top list
	while date_obj < datetime.datetime.now().date() + datetime.timedelta(days=7):
		print('Getting songs for ' + str(date_obj) + '...\n')

		#Try to fetch the url and restart the connection if it times out (loop without changing date)
		try:
			async with aiohttp.ClientSession(timeout = timeout) as session:
				html = await fetch(session, url)
		except:
			print('Timeout. Restarting connection...\n')
			timeouts += 1
			continue

		# HTML parsing
		page_soup = soup(html, "html.parser")

		#Get songs, artists, and date
		songs = page_soup.select('span[class=chart-list-item__title-text]')
		artists = page_soup.select('div[class=chart-list-item__artist]')
		date = page_soup.select('button[class=chart-detail-header__date-selector-button]')

		date_str = date[0].get_text().strip()
		date_on_page = datetime.datetime.strptime(date_str, '%B %d, %Y').date()

		#Account for date mismatches
		if date_obj != date_on_page:
			date_obj = date_on_page
			print('Date mismatch. Changing date to ' + str(date_obj) + '...\n')
			date_changes += 1

		#Append with song and artist names
		week = {}
		week['Week'] = str(date_obj)
		for i in range(len(songs)):
			week[i+1] = [songs[i].get_text().strip(), artists[i].get_text().strip()]

		num_errors = 0

		if bool(week):
			print('Data gathered.\n')
		else:
			print('Data empty!\n')
			num_errors += 1

		#Save to file
		data.append(week)
		print('Data saved to file.\n')
		with open(fname, 'wb') as f:
			pickle.dump(data, f)

		#Update date and url
		date_obj += datetime.timedelta(days=7)
		url = 'https://www.billboard.com/charts/hot-100/' + str(date_obj)

	print(f'All done! {num_errors} errors, {timeouts} timeouts, and {date_changes} date mismatches encountered.\n')

#Start process
loop = asyncio.get_event_loop()
loop.run_until_complete(main())