
import requests
# import json
from bs4 import BeautifulSoup
import csv
import psycopg2


class RfgfCatalogInvestigator():
    '''
    this is a class to investigate the contents of https://rfgf.ru/catalog/index.php website
    '''
    def __init__(self):
        pass

    def request_reports(self, **kwargs):
        """
        This function makes request to rfgf.ru/catalog/index.php website and returns the result
        from all or from requested pages of the result as dictionary and optionally writes the result to csv file.
        :param kwargs:
        ftext='some text' - mandatory. Search string for the request.
        out_csv='path to output csv' - optional. Path to result csv file. The default is null, which means not to write output file.
        start_page=number - optional. Number of the first request result page to process. The default is 1.
        end_page=number - optional. Number of the last request result page to process. The default is the last page.
        :return:
        The function returns the dictionary with search results from rfgf.ru/catalog/index.php website.
        If out_csv='path to output csv' is specified, the result will be written to the file too.
        """
        # this makes the request to rfgf catalog. The structure of request is hacked from Chrome F12 mode.
        # first kwargs['ftext'] parameter is used as a search string.
        response = requests.post('https://rfgf.ru/catalog/index.php',
                                 headers={'accept': '*/*',
                                          'accept-encoding': 'gzip, deflate, br',
                                          'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                                          'Connection': 'keep-alive',
                                          'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                          # 'cookie': 'PHPSESSID=c46b455dd42f1126c309c3aadbd03d62; selfpath=/catalog/index.php; detalied=1; _ym_uid=1658903758737911296; _ym_d=1658903758; _ym_isad=2; _ym_visorc=w',
                                          'dnt': '1'
                                          },
                                 data={
                                     'ftext': kwargs['ftext'],
                                     'search': '0',
                                     'docname': '',
                                     'authors': '',
                                     'invn': '',
                                     'nom': '',
                                     'pnum': '',
                                     'pdate': '',
                                     'penddate': '',
                                     'year': '',
                                     'place': '',
                                     'full': '1',
                                     'gg': '',
                                     'mode': 'limctl',
                                     'orgisp': '',
                                     'source': '',
                                     'pi': ''
                                 }
                                 )
        # parse the html result of the request with BeautifulSoup parser
        soup = BeautifulSoup(response.text, 'html.parser')
        # this is the default number of pages to process
        pages = 1
        # now let's find how many pages the result has
        # check if the result is not empty
        if 'Поиск не дал результатов' not in soup.text:
            # find the <ul class="hr2" id="list_pages2"> tag which contains the number of pages, then loop through the <li> tags in it
            for li in soup.find(id='list_pages2').find_all('li'):
                # if 'из' is in the tag text, then whe are inside the desired tag
                if li.text.find('из') > 0:
                    # take the tag text and remove anything but the numbers from it
                    pages = int(str(li.text[li.text.find('из') + 3:].replace('>', '').replace(' ', '')))
                    # print(pages)


            # create an empty list for the reports. Each report will be appended here as dictionary
            reports = []
            # Flag to write output to csv or not
            write_csv = False
            # If more than one arg is specified, we assume that csv must be written
            if 'out_csv' in kwargs.keys() and len(kwargs['out_csv']) > 1:
                write_csv = True
            # open csv file for writing if write_csv is True
            if write_csv:
                csvfile = open(kwargs['out_csv'], 'w', newline='', encoding='utf-8')

            # this loop is to discover the field names only
            # find the html tag with id='report_table' and then loop through all tables in it
            fields = []
            for report_table in soup.find(id='report_table').find_all('table'):
                # create empty lists for field names and for the values
                # fields = []
                values = []
                # find the html table with class='report'. This is usually the table with all search results on the page
                if report_table['class'] == ['report']:
                    # start the row counter for the report table
                    row_counter = 0
                    # loop through all rows of the table
                    for row in report_table.find_all('tr'):
                        # iterate row counter
                        row_counter += 1
                        # This <if> section is to create the fieldnames list.
                        # check if we are in the 'head' row.
                        if 'class' in row.attrs.keys() and row['class'] == ['head']:
                            # start the cells counter
                            td_counter = 0
                            # loop through all cells in a row
                            for td in row.find_all('td'):
                                # iterate cells counter
                                td_counter += 1
                                # the first cell is always blank, so we'll skip it
                                if td_counter > 1:
                                    # There are two head rows in the table. All cells are rowspanned except the
                                    # Предметно-систематический классификатор.
                                    # so we check if we are in this cell and therefore add two fieldnames
                                    # Раздел and Подраздел to the list
                                    if td.text == 'Предметно-систематический классификатор':
                                        fields.append('Раздел')
                                        fields.append('Подраздел')
                                    # if we are in any other cell in two head rows except Раздел and Подраздел,
                                    # add its value to the list of fieldnames.
                                    elif td.text not in ('Раздел', 'Подраздел'):
                                        fields.append(td.text)
                            # if we've passed through both head rows
                            if row_counter == 2:
                                # add additional fieldname for the url to this report
                                fields.append('Ссылка')
                                # now we've passed through the header rows, and it's time to create
                                # the DictWriter for the csv file if we need it
                                if write_csv:
                                    writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter='|')
                                    # write csv header to the output file
                                    writer.writeheader()

            reports_written_counter = 0

            #################################################################################################################
            # this loop is to discover the data itself, looping through the pages of the result
            # the defaut start page
            start = 1
            # if the start page is specified in **kwargs, then use it
            if 'start_page' in kwargs.keys() and kwargs['start_page'] and type(kwargs['start_page'] == int):
                start = kwargs['start_page']
            # the default end page is the total number of pages. if the start page is specified in **kwargs, then use it
            if 'end_page' in kwargs.keys() and kwargs['end_page'] and type(kwargs['end_page'] == int):
                pages = kwargs['end_page']
            # loop through the pages of the result
            for i in range(start, pages + 1):
                # make http post request to the current page of the result
                new_response = requests.post('https://rfgf.ru/catalog/index.php',
                                         headers={'accept': '*/*',
                                                  'accept-encoding': 'gzip, deflate, br',
                                                  'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                                                  'Connection': 'keep-alive',
                                                  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                                  # 'cookie': 'PHPSESSID=c46b455dd42f1126c309c3aadbd03d62; selfpath=/catalog/index.php; detalied=1; _ym_uid=1658903758737911296; _ym_d=1658903758; _ym_isad=2; _ym_visorc=w',
                                                  'dnt': '1'
                                                  },
                                         data={
                                             'ftext': kwargs['ftext'],
                                             'search': '0',
                                             'docname': '',
                                             'authors': '',
                                             'invn': '',
                                             'nom': '',
                                             'pnum': '',
                                             'pdate': '',
                                             'penddate': '',
                                             'year': '',
                                             'place': '',
                                             'full': '1',
                                             'gg': '',
                                             'mode': 'limctl',
                                             'orgisp': '',
                                             'source': '',
                                             'pi': '',
                                             # this is the page number
                                             'page': str(i)
                                         }
                                         )
                # create new BeautifulSoup from the current page
                new_soup = BeautifulSoup(new_response.text, 'html.parser')
                # loop through all the tables in <div id="report_table"> tag
                for new_report_table in new_soup.find(id='report_table').find_all('table'):
                    # create empty lists for the values
                    values = []
                    # find the html table with class='report'. This is usually the table with all search results on the page
                    if new_report_table['class'] == ['report']:
                        # start the row counter for the report table
                        row_counter = 0
                        # loop through all rows of the table
                        for row in new_report_table.find_all('tr'):
                            # iterate row counter
                            row_counter += 1
                            # if we are not in the table head
                            if not ('class' in row.attrs.keys() and row['class'] == ['head']):
                                # start new cell-in-a-row counter
                                td_counter = 0
                                # string for the link to this report in the catalog
                                link = ''
                                # loop through all cells in a row
                                for td in row.find_all('td'):
                                    # There are rows with colspan=21, which we don't need. Check if we are not in it.
                                    if not ('colspan' in td.attrs.keys() and td['colspan'] == '21'):
                                        # iterate cell counter
                                        td_counter += 1
                                        # we don't need the data from the first cell
                                        if td_counter > 1:
                                            # if we are in the 10-th cell, which is for the
                                            # 'Доступен для загрузки через реестр ЕФГИ',
                                            # and the link exists in the cell (<a href=....>Да</a> hyperlink)
                                            # then write the url from the <a> instead of the text
                                            if td_counter == 10:
                                                if 'Да' in td.text:
                                                    values.append('https://rfgf.ru/catalog/' + td.a['href'])
                                                # If there is no link in the cell, write just the text
                                                else:
                                                    values.append(td.text.replace('\n', '').replace('\r', '').rstrip())
                                            # if we are in the 8-1th cell, which is the 'Есть сканобраз' column,
                                            # then we again take the url from <a> and append an ending to it
                                            elif td_counter == 8:
                                                if 'Да' in td.text:
                                                    values.append(
                                                        'https://rfgf.ru/catalog/' + td.a['href'] + '&dtype=1#refancor')
                                                # if cell 8 is empty, add just the text
                                                else:
                                                    values.append(td.text.replace('\n', '').replace('\r', '').rstrip())
                                            # if we are in any cell other than 1, 8 or 10, just write the cell value to the list
                                            else:
                                                values.append(td.text.replace('\n', '').replace('\r', '').rstrip())
                                        # take the report url from the 2nd cell's href attribute
                                        if td_counter == 2:
                                            link = td.a['href']
                                # add the link of the report as the last value to the list
                                values.append(link.replace('./', 'https://rfgf.ru/catalog/'))
                                # if we have any values from the row
                                if len(values) > 1:
                                    # create the current report dictionary and append it to the result list
                                    reports.append({fields[i]: values[i] for i in range(len(fields))})
                                    # if we must create the output csv
                                    if write_csv:
                                        # add new data line to output csv
                                        writer.writerow({fields[i]: values[i] for i in range(len(fields))})
                                        # iterate the written reports counter
                                        reports_written_counter += 1
                                        # print message for every 100 reports written
                                        if reports_written_counter % 100 == 0:
                                            print(reports_written_counter, 'reports processed')
                                # empty the values list for the next row loop
                                values = []

            #################################################################################################################


            # close the output csv file if we opened it
            if write_csv:
                csvfile.close()
                # print the total number of reports processed
                # print(reports_written_counter, 'reports processed')
            # return the dictionary of reports
            return reports
        # in case of empty search result print message and return empty list
        else:
            # print('Empty result')
            return []




# This is an example of using the class.
# first you create an instance of RfgfCatalogInvestigator.
# second, you call it's request_reports function to download the data from rfgf.ru/catalog/index.php
# You must specify the search string in ftext parameter, and you may specify the output csv in out_csv parameter,
# the start page to download in start_page parameter and the last page to download in end_page parameter.
# To understand what these pages mean, you can go to rfgf.ru/catalog/index.php website, make search with an empty search string (for example).
# Then at the bottom of the page you'll see the result pages switcher. These are the page numbers for start_page and end_page parameters.
# When there are thousands of pages, it may be convenient to split the request in several parts, downloading limited number of pages at a time.
# If you want to download all the results at one time, just skip the startpage and end_page parameters.

my_investigator = RfgfCatalogInvestigator()
# reports = my_investigator.request_reports(ftext='496', out_csv='all_reports_from_rfgf_part6.csv', start_page=1, end_page=2)
# reports = my_investigator.request_reports(ftext='', out_csv='all_reports_from_rfgf_20230911_part1.csv', start_page=1, end_page=4690)
# reports = my_investigator.request_reports(ftext='', out_csv='all_reports_from_rfgf_20230911_part2.csv', start_page=4691, end_page=9380)
# reports = my_investigator.request_reports(ftext='', out_csv='all_reports_from_rfgf_20230911_part3.csv', start_page=9381, end_page=14070)
# reports = my_investigator.request_reports(ftext='', out_csv='all_reports_from_rfgf_20230911_part4.csv', start_page=14071, end_page=18760)
# reports = my_investigator.request_reports(ftext='', out_csv='all_reports_from_rfgf_20230911_part5.csv', start_page=18761, end_page=23450)
# reports = my_investigator.request_reports(ftext='', out_csv='all_reports_from_rfgf_20230911_part6.csv', start_page=23451)



# with open('.pgdsn', encoding='utf-8') as f:
#     pgcs = f.read().replace('\n', '')
#
# with psycopg2.connect(pgcs) as pgconn:
#     # input_files = ['all_reports_from_rfgf_20230911_part2.csv']
#     input_files = ['all_reports_from_rfgf_20230911_part3.csv',
#                    'all_reports_from_rfgf_20230911_part4.csv',
#                    'all_reports_from_rfgf_20230911_part5.csv',
#                    'all_reports_from_rfgf_20230911_part6.csv']
#     with pgconn.cursor() as cur:
#         for i_f in input_files:
#             with open(i_f, encoding='utf-8', newline='') as f:
#                 reader = csv.DictReader(f, delimiter='|')
#                 for i, row in enumerate(reader):
#                     fields_to_update = ['"' + x + '"' for x in row.keys()]
#                     values_to_insert = ["'" + x.replace("'", "''") + "'" for x in row.values()]
#                     sql = f"insert into rfgf.rfgf_catalog_20230911({', '.join(fields_to_update)}) values({', '.join(values_to_insert)});"
#                     cur.execute(sql)
#                     if i % 10000 == 0:
#                         print (f"{str(i)} records committed")
#                         pgconn.commit()
