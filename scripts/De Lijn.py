from scripts.Agency import Agency
import overpy
import os
from requests import post
import re

use_test_data = False
download_again = True

#(._;<;);
# query = '''
# [out:xml][timeout:590];
# (
#   relation["operator"="De Lijn"];
# );
#
# (._;>>;);
# out meta;'''

public_identifier = '598'
public_identifier = '305'
agency_identifier = ''
if public_identifier:
    public_identifier = f'["ref"="{public_identifier}"]'
if agency_identifier:
    agency_identifier = f'["ref:De_Lijn"="{agency_identifier}"]'
query = f'''
[out:xml][timeout:290];
(
  relation["operator"="De Lijn"]{public_identifier}{agency_identifier};
);

(._;>>;);
out meta;'''

fn = os.path.join(os.path.split(os.getcwd())[0],'test_data', 'DeLijn.osm')

specific_tags = {}
for t in ['ref', 'route_ref', 'zone']:
    specific_tags[t] = t + ':De_Lijn'

wikidata = {'De Lijn': 'Q614819',
            'DlAn': 'Q34803327',
            'DlOV': 'Q34803340',
            'DlVB': 'Q34803298',
            'DlLi': 'Q34803313',
            'DlWV': 'Q34803353',
            }
delijn = Agency(name='De Lijn',
                sheet_url=("https://docs.google.com/spreadsheet/ccc"
                           "?key=1PGgEqobO90Mf9NsJHO1-JD-Npte1fYztK30HO5lRDI8"
                           "&output=xls"),
                operator_specific_tags=specific_tags,
                shorten_stop_name_regex=re.compile(r"""(?xiu)
                                                       (?P<name>[\s*\S]+?)
                                                       (?P<platform>\s*-?\s*perron\s*\d+(\sen\s\d+)*)?
                                                       $"""),
                url_for_stops="mijnlijn.be/{stopidentifier}",
                url_for_lines="https://www.delijn.be/nl/lijnen/lijn/{routeidentifier[0]}/{routeidentifier[1:]}",
                url_for_itineraries="https://www.delijn.be/nl/lijnen/lijn/{routeidentifier[0]}/{routeidentifier[1:]}",
                networks={1: 'An',
                          2: 'OV',
                          3: 'VB',
                          4: 'Li',
                          5: 'WV'},
                wikidata = wikidata,
                )

if download_again:
    print('Downloading OSM data to file')
    response = post("http://overpass-api.de/api/interpreter", query)
    print(response)
    with open(fn, 'wb') as fh:
        fh.write(response.content)

api = overpy.Overpass()
if use_test_data:
    print("reading OSM file")
    with open(fn) as fh:
        osm_data = api.parse_xml(data=fh.read(),
                                 encoding='utf-8',
                                 parser=None)
else:
    print("downloading data directly from Overpass API")
    osm_data = api.query(query)

delijn.process_query_result(osm_data, public_identifier=public_identifier, agency_identifier=agency_identifier)

delijn.fetch_agency_data()
delijn.load_agency_data()
delijn.update_using_operator_data()
delijn.send_to_josm()
