# RfgfCatalogInvestigator
This is a python script to download the complete or partial catalog of geologic documents from Rosgeolfond website https://rfgf.ru/catalog/index.php into csv file.

The class RfgfCatalogInvestigator creates an object that can download the data with its methods.

The method RfgfCatalogInvestigator.request_reports(self, **kwargs) is the function to request and download the search results from https://rfgf.ru/catalog/index.php website. The detailed description of this method is given inside its infostring and below:
        :param kwargs:
        ftext='<some text>' - mandatory. Search string for the request.
        out_csv='<path to output csv>' - optional. Path to result csv file. The default is null, which means not to write output file.
        start_page=<number> - optional. Number of the first request result page to process. The default is 1.
        end_page=<number> - optional. Number of the last request result page to process. The default is the last page.
        :return:
        The function returns the dictionary with search results from rfgf.ru/catalog/index.php website.
        If out_csv='<path to output csv>' is specified, the result will be written to the file too.
        """

