# Create Address Labels

This will take a CSV file with addresses and create labels. The labels will be formatted for each country, and will be sized to fit on the label itself. To create a PDF with labels in your address book, you will need to export the addressbook as a CSV file, and run `python main.py`. This will generate an output file called `labels.pdf` with all your addresses formatted for Avery 5160 labels. You can print this file and attach the labels to your cards.

# Input Files

The program uses 4 files as input, and a single file as output:

| filename       | description                                                  |
| -------------- | ------------------------------------------------------------ |
| countries.json | list of formattings for countries, this will use the keys from the tsv file to format the label. |
| example.tsv    | file with example addresses, goal is to have one address per country. |
| labels.tsv     | list of labels, their size and other characteristics of the labels. |
| mappings.json  | mapping from column names to keys used in the application.   |

## Keys used in the code

You will need to map your tsv address book to keys that are used in the application. The `example.tsv` file will show you a simple spreadsheet that can be used with the default `mappings.json`. The following keys are used:

| key        | meaning                                                      |
| ---------- | ------------------------------------------------------------ |
| firstname  | First name of the person                                     |
| lastname   | Last name, of family name, of the person                     |
| fullname   | Fully formatted name, if this is blank it will be created by concattenating first and last name |
| address1   | First address line (such as street)                          |
| address2   | Second address line (such as apartment)                      |
| address3   | Third address line                                           |
| city       | The city of the person                                       |
| state      | The state, or province, or any other larger scope that city. |
| postalcode | The postalcode or zipcode for the address                    |
| country    | The country for the address, this will be used for formatting the address |

# Application Arguments

The application takes the following arguments (all of them will have defaults)

| argument                                                     | description              | default |
| ------------------------------------------------------------ | ------------------------ | ------- |
| --help<br />-h |show this help message and exit | |
| --labels [LABELS]<br />-l [LABELS] | file with label definitions | labels.tsv |
| --brand [BRAND]<br />-b [BRAND]                              | brand for address labels | Avery   |
| --number [NUMBER]<br />-n [NUMBER] | label to use for printing | 5160 |
| --padding [PADDING]<br />-p [PADDING] | extra padding inside the label | 4 |
| --font [FONT]<br />-f [FONT] | font to use for label | Times-Roman |
| --drawbox<br />-d |draw a box around the label | false |
| --input [INPUT]<br />-i [INPUT] | tsv file with addresses | address.tsv |
| --mappings [MAPPINGS]<br />-m [MAPPINGS] | file with mappings from tsv to address format | mappings.json |
| --country [COUNTRY]<br/>-c [COUNTRY] |country to not add to label and use for addresses with no country specified | USA |
| --output [OUTPUT]<br />-o [OUTPUT] | pdf file that labels are written to | labels.pdf |
