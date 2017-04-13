from lxml import html
import requests


# Substitute for the group requested name
name = "Porcupine Tree"
formatted_name="+".join(name.split())

base_page = 'https://musicbrainz.org'
results_page = requests.get(base_page + '/search?query=' + formatted_name + '&type=artist')
tree = html.fromstring(results_page.content)


first_result = tree.xpath('//table[@class="tbl"]')[0].xpath('//tbody//tr//td//a')[0].values()[0]
artist_url = base_page + first_result


#####################################################
# Scraps description of the group
#####################################################
overview_page = requests.get(artist_url)
overview_tree = html.fromstring(overview_page.content)
description = overview_tree.xpath('//div[@class="wikipedia-extract-body wikipedia-extract-collapse"]')
# Wikipedia description for the group
description = description[0].text_content()



#####################################################
# Scraps members of the group
#####################################################
rel_page = requests.get(artist_url + '/relationships')
rel_tree = html.fromstring(rel_page.content)
members = rel_tree.xpath('//table[@class="details"]')[0]
actual_members_tags = members[0].xpath('td//a')
former_members_tags = members[1].xpath('td//a')

actual_members = [ m.text_content() for m in actual_members_tags ]
former_members = [ m.text_content() for m in former_members_tags ]
