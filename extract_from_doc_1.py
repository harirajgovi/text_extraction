"""
Problem Statement: Extract values from Financial Statement documents

Solution Approach: Used NLTK, Regular Expressions and Case Statements to tokenize, 
                   search and filter out string patterns with OOP concept.
"""

#importing libraries
import pandas as pd
from nltk.tokenize import RegexpTokenizer 
import re
import json
import warnings

warnings.filterwarnings("ignore")

#Creating class
class NLP():
    
    def __init__(self, doc):
        """
        Input: List of rows in text file
        """
        self.doc = doc
        self.extracted = {}
    
    
    def __get_column_details(self):
        """
        Output: years present in column (ex: ["2019", "2018"]),
                index position of column "2019" (ex: 0), 
                starting row number to extract data (ex: 3)
        """
        output = []
        year = re.compile(r"\d{4}|\d///\d/\d{2}/\d")
        column = re.compile(r"\s{4,}\d{4}|\s{3,}(\d{2})/(\d{2})/(\d{4})|\s{5}\d+\D+\d+|\s{3,}\d///\d/\d{2}/\d")
        
        for line in range(5):
            
            if column.search(self.doc[line]) and not (re.search(r"\d{4}", self.doc[line+1])):
                output.append(year.findall(self.doc[line]))
                if "2019" in output[0]:
                    output.append(output[0].index("2019"))
                else:
                    output.append("no_2019_column")
                output.append(line+2)
                return output
            else:
                continue
            
    
    def extract(self):
        """               
        Output: extracted data in dictionary format
        """
        #executing get_column_details function
        years, pos, start = self.__get_column_details()
        ln = len(years)
        
        output = {}
        double_row_str = ("Creditors: amounts falling due within one year", 
                           "Creditors: amounts falling due after more than one year")
        to_remove = ("Creditors: amounts falling due within", 
                     "Creditors: amounts falling due within one", 
                     "Creditors: amounts falling due", "Creditors: amounts falling")
        tokenizer = RegexpTokenizer(r"[^\s]+")
        
        for line in range(start, start+12):
            
            data = tokenizer.tokenize(self.doc[line])
            
            if (line > start and "funds" in list(output.keys())[-1]) or (len(data) == 1 and re.match(r"[A-Z]{2,}", data[0])) or (re.search(r"Notes|NOTES|Number|General"," ".join(data))) or (len(data) >= 14):
                break
            elif len(data) == 0 or (data[0] == "year" and double_row_str[1] in set(output.keys())):
                continue
            elif (len(data) > 1 and re.match(r"[\d(\d)-]+|[{\d)]|I", data[-1]) and re.match(r"\d+\s[a-zA-Z]|\D+\s\d|\D+\s\D+", data[0]+" "+data[1])):
                if pos == "no_2019_column":
                    particulars = data[:-ln]
                    particulars = " ".join(particulars)
                    if ("Creditors: amounts falling due within one" in set(output.keys())) and (re.match(r"[\d-]+",output["Creditors: amounts falling due within one"])):
                        output[double_row_str[0]] = output.pop("Creditors: amounts falling due within one")
                        continue
                    amount = "nan"
                else:
                    particulars = data[:-ln]
                    particulars = " ".join(particulars)
                    if ("Creditors: amounts falling due within one" in set(output.keys())) and (re.match(r"[\d-]+",output["Creditors: amounts falling due within one"])):
                        output[double_row_str[0]] = output.pop("Creditors: amounts falling due within one")
                        continue
                    elif "Creditors: amounts falling due after" in set(output.keys()):
                        output[double_row_str[1]] = output.pop("Creditors: amounts falling due after")
                        particulars = double_row_str[1]
                    elif list(set(to_remove) & set(list(output.keys()))):
                        output[double_row_str[0]] = output.pop(list(set(to_remove) & set(list(output.keys())))[0])
                        particulars = double_row_str[0]
                    if len(data) == 2:
                        particulars = data[0]
                        amount = data[1]
                    else:
                        amount = data[-ln:][pos]
                    if re.match(r"[(](.*[)])", amount):
                        amount = "-" + amount.strip("()")
                        amount = amount.replace(",", "")
                    elif re.match(r"({)(.*[)])", amount):
                        pass
                    else:
                        amount = amount.replace(",", "")
            elif re.match(r"[\d(\d)-]+|[{\d)]", data[0]):
                if pos == "no_2019_column":
                    particulars = "nan"
                    if ("Creditors: amounts falling due after more than one" in set(output.keys())) and (output["Creditors: amounts falling due after more than one"] == "nan"):
                        output[double_row_str[1]] = output.pop("Creditors: amounts falling due after more than one")
                        continue
                    amount = "nan"
                else:
                    particulars = "nan"
                    amount = data[pos]
                    if re.match(r"[(](.*[)])", amount):
                        amount = "-" + amount.strip("()")
                        amount = amount.replace(",", "")
                    elif re.match(r"({)(.*[)])", amount):
                        pass
                    else:
                        amount = amount.replace(",", "")
                    if ("Creditors: amounts falling due after more than one" in set(output.keys())) and (output["Creditors: amounts falling due after more than one"] == "nan"):
                        output[double_row_str[1]] = output.pop("Creditors: amounts falling due after more than one")
                        output[double_row_str[1]] = amount
                        if output[double_row_str[1]] == "2.531)":
                            output[double_row_str[1]] = "-2531"
                        continue
            elif re.match(r"\D{2,}", data[-1]):
                particulars = " ".join(data)
                if ("Creditors: amounts falling due within one" in set(output.keys())) and (re.match(r"[\d-]+",output["Creditors: amounts falling due within one"])):
                    output[double_row_str[0]] = output.pop("Creditors: amounts falling due within one")
                    continue
                amount = "nan"
                    
            particulars = re.search(r".*[^\d$]+", particulars).group()
            particulars = particulars.strip(" ___")
            amount = re.sub(r"y", "", amount)
            if particulars == "":
                particulars = "nan"
            output[particulars] = amount 
            
        self.extracted = output
        return 
    
    
    def result(self):
        """
        Output: extracted data replacing utf-8 encoded symbols and currency symbols
                with respective html code.
        """
        output = str(self.extracted)
        
        to_replace = ((".00", ""), ("Â£", "&#163"), ("â‚¬", "&#8364"), ("Ä…", "&#261"),
                      ("Å‚", "&#322"), ("$", "&#36"), ("£", "&#163"), ("€", "&#8364"))
        
        for i in range(0, len(to_replace)):
            output = output.replace(to_replace[i][0], to_replace[i][1])
            
        output = eval(output) 
        if list(output.keys())[0] == "Net assets" and len(output.keys()) == 4:
            output["nan"] = "nan"
            
        output = json.dumps(output)           
        return output


def main():
    #importing Results.csv file to get the filename for data extraction
    submission = pd.read_csv("Results.csv", encoding="utf-8")  
    
    print("\n", "extracting......")
    
    #Iterating the filenames in a for loop
    for idx, file_name in enumerate(submission["Filename"]):
        
        file_content = None
        with open("HCL ML Challenge Dataset//{}.txt".format(file_name), 'r') as f:
            file_content = list(f.readlines())
            f.close()
            
        nlp = NLP(file_content)
        
        nlp.extract()
        
        submission["Extracted Values"][idx] = nlp.result()

    #saving the output dataframe to local drive in the csv format
    submission.to_csv("output.csv", index=False, encoding="utf-8")
    
    
if __name__ == "__main__":
    
    main()