# RfgfCatalogInvestigator
This is a python script to download the complete or partial catalog of geologic documents from Rosgeolfond website https://rfgf.ru/catalog/index.php into csv file.

The class RfgfCatalogInvestigator creates an object that can download the data with its methods.

The method RfgfCatalogInvestigator.request_reports(self, **kwargs) is the function to request and download the search results from https://rfgf.ru/catalog/index.php website. The detailed description of this method is given inside its infostring and below:

:param kwargs:
ftext='<some text>' - mandatory. Search string for the request.
out_csv='path to output csv' - optional. Path to result csv file. The default is null, which means not to write output file.
start_page=number - optional. Number of the first request result page to process. The default is 1.
end_page=number - optional. Number of the last request result page to process. The default is the last page.
:return:
The function returns the dictionary with search results from rfgf.ru/catalog/index.php website.
If out_csv='path to output csv' is specified, the result will be written to the file too.

 first you create an instance of RfgfCatalogInvestigator.
 second, you call it's request_reports function to download the data from rfgf.ru/catalog/index.php
 You must specify the search string in ftext parameter, and you may specify the output csv in out_csv parameter,
 the start page to download in start_page parameter and the last page to download in end_page parameter.
 To understand what these pages mean, you can go to rfgf.ru/catalog/index.php website, make search with an empty search string (for example).
 Then at the bottom of the page you'll see the result pages switcher. These are the page numbers for start_page and end_page parameters.
 When there are thousands of pages, it may be convenient to split the request in several parts, downloading limited number of pages at a time.
 If you want to download all the results at one time, just skip the startpage and end_page parameters.



Here are the examples of usage:
 
 
1. create an instance of RfgfCatalogInvestigator class

my_investigator = RfgfCatalogInvestigator()


2. use request_reports method to get all the search results for "498561" request and write them to 498561.csv file

reports = my_investigator.request_reports(ftext='498561', out_csv='498561.csv')


3. use request_reports method to get the full content of the catalog to the all_reports.csv file. This is over 1.3 million records
and 1.3 GB of data, so you Internet connection must be stable:

reports = my_investigator.request_reports(ftext='', out_csv='all_reports.csv')


4. use request methods to get the full content of the catalog in several parts. You can make the search on website first to know the 
total number of pages in the result. For example, if there are 26768 pages in the final result:

reports = my_investigator.request_reports(ftext='', out_csv='all_reports_part1.csv', start_page=1, end_page=5000)
         
reports = my_investigator.request_reports(ftext='', out_csv='all_reports_part2.csv', start_page=5001, end_page=10000)
         
reports = my_investigator.request_reports(ftext='', out_csv='all_reports_part3.csv', start_page=10001, end_page=15000)
         
reports = my_investigator.request_reports(ftext='', out_csv='all_reports_part4.csv', start_page=15001, end_page=20000)
         
reports = my_investigator.request_reports(ftext='', out_csv='all_reports_part5.csv', start_page=20001, end_page=25000)
         
reports = my_investigator.request_reports(ftext='', out_csv='all_reports_part6.csv', start_page=25001, end_page=26768)

you will have 6 separate csv files which you can later merge together manually.
Remember, that first line is always th field names!
