#!/usr/bin/env python

import argparse
import csv
import json

from reportlab.lib.colors import black
from reportlab.lib.units import toLength
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def print_label(canvas, font, fontsizes, padding, data, label, count, drawlabel):
    x = label["margin"]["left"] + \
        count % label["across"] * (label["size"]["width"] + label["padding"]["left"])
    y = label["margin"]["top"] + \
        count // label["across"] * (label["size"]["height"] + label["padding"]["top"])

    name = data[0]
    for size in fontsizes:
        canvas.setFont(font, size)
        if canvas.stringWidth(name) <= label["size"]["width"] - (2 * padding):
            break
    else:
        center = len(name) // 2
        plusminus = 0
        while plusminus < center and name[center + plusminus] != " " and name[center - plusminus] != " ":
            plusminus += 1
        if name[center + plusminus] == " ":
            data[0] = name[center + plusminus + 1:]
            data.insert(0, name[:center + plusminus])
        else:
            data[0] = name[center - plusminus + 1:]
            data.insert(0, name[:center - plusminus])

    for size in fontsizes:
        if (label["size"]["height"] - 2 * padding) / len(data) >= size:
            for line in data:
                canvas.setFont(font, size)
                if canvas.stringWidth(line) > label["size"]["width"] - (2 * padding):
                    break
            else:
                break
    else:
        size = int(label["size"]["height"] - 2 * padding) // len(data)
    canvas.setFont(font, size)

    offset = 0
    for line in data:
        canvas.drawString(padding + x, label["paper"]["height"] - y - offset - size - padding / 2, line)
        offset += size

    if drawlabel:
        canvas.rect(x, label["paper"]["height"] - y,
                    label["size"]["width"], -label["size"]["height"], fill=0)


def format_address(address, countries, country):
    """
    Format the address based on country. Different countries format
    addresses differently, stay as close as possible to the
    formatting for each country.

    :param address: dictionary with the name and address of the recipient.
    :param countries: how to format the address for a specific country.
    :param country: country to use as default and not add to label
    :return: array of strings with the formatted address, or None if nothing is left.
    """

    rows = [address["name"]]

    if address['country']:
        address_country = address['country'].lower()
    else:
        print(f"Missing country for {address['name']}, assuming {country}.")
        address_country = country.lower()

    homeformatter = None
    for formatter in countries:
        if not homeformatter and country.lower() in formatter['country']:
            homeformatter = formatter
        if address_country in formatter["country"]:
            if country.lower() in formatter['country']:
                address['country'] = ""
            for f in formatter['format']:
                rows.append(f.format(**address))
            break
    else:
        print(f"No formatter found for {address['country']}")
        if homeformatter:
            for f in homeformatter['format']:
                rows.append(f.format(**address))

    # remove empty lines
    result = []
    for line in rows:
        line = line.strip().strip(",")
        if line:
            result.append(line)

    # if empty, just return None
    if result:
        return result
    else:
        return None


def get_field(header, row, name, default=""):
    try:
        return row[header.index(name)]
    except ValueError:
        pass
    except IndexError:
        pass
    return default


def get_name(header, row):
    """
    Given the tsv file, return the name. The name is either display
    name, full name, or concatenation of first and last name.
    :param header: header of the tsv file to find column names.
    :param row: the row with the address information.
    :return: the full name of the person to print.
    """

    name = get_field(header, row, "fullname")

    if not name:
        # combine first and last name
        firstname = get_field(header, row, "firstname")
        lastname = get_field(header, row, "lastname")
        name = " ".join([firstname, lastname])

    return name


def get_address(header, row):
    return {
        "name": get_name(header, row),
        "address1": get_field(header, row, "address1"),
        "address2": get_field(header, row, "address2"),
        "address3": get_field(header, row, "address3"),
        "postalcode": get_field(header, row, "postalcode"),
        "city": get_field(header, row, "city"),
        "state": get_field(header, row, "state"),
        "country": get_field(header, row, "country"),
    }


def load_label(filename, brand, number):
    header = None
    with open(filename, newline='') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t', quotechar='"')
        for row in reader:
            if not header:
                header = row
                continue
            if row[0].lower() == brand.lower() and row[1].lower() == number.lower():
                return {
                    "across": int(row[2]),
                    "down": int(row[3]),
                    "size": {
                        "width": toLength(row[4]),
                        "height": toLength(row[5]),
                    },
                    "padding": {
                        "left": toLength(row[6]),
                        "top": toLength(row[7]),
                    },
                    "paper": {
                        "width": toLength(row[8]),
                        "height": toLength(row[9]),
                    },
                    "margin": {
                        "left": toLength(row[10]),
                        "top": toLength(row[11]),
                    },
                }

    raise ValueError(f"Could not find {brand} {number} amongst labels.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--brand', '-b', type=str, nargs='?', default="Avery",
                        help='brand for address labels (Avery)')
    parser.add_argument('--country', '-c', type=str, nargs='?', default="USA",
                        help='country to not add to label and use for addresses with no country specified')
    parser.add_argument('--drawbox', '-d', action='store_true',
                        help='draw a box around the label')
    parser.add_argument('--font', '-f', type=str, nargs='?', default="Times-Roman",
                        help='font to use for label ("Times-Roman")')
    parser.add_argument('--input', '-i', type=str, nargs='?', default="address.tsv",
                        help='tsv file with addresses (address.tsv)')
    parser.add_argument('--labels', '-l', type=str, nargs='?', default="labels.tsv",
                        help='file with label definitions (labels.tsv)')
    parser.add_argument('--mappings', '-m', type=str, nargs='?', default="mappings.json",
                        help='file with mappings from tsv to address format')
    parser.add_argument('--number', '-n', type=str, nargs='?', default="5160",
                        help='label to use for printing (5160)')
    parser.add_argument('--output', '-o', type=str, nargs='?', default="labels.pdf",
                        help='pdf file that labels are written to (labels.pdf)')
    parser.add_argument('--padding', '-p', type=str, nargs='?', default="4",
                        help='extra padding inside the label (4)')
    args = parser.parse_args()

    # find the label
    label = load_label(args.labels, args.brand, args.number)

    # load country mappings
    countries = json.load(open("countries.json", "r"))
    for x in countries:
        x["country"] = [s.lower() for s in x["country"]]

    padding = 4
    fontsizes = [16, 14, 12]

    # create the canvas
    canvas = Canvas(args.output, pagesize=(label["paper"]["width"], label["paper"]["height"]))
    canvas.setFillColor(black)

    # load font, or use default font
    font = args.font
    if font not in canvas.getAvailableFonts():
        for ext in ['ttf', 'ttc']:
            try:
                pdfmetrics.registerFont(TTFont(font, f'{font}.{ext}'))
                break
            except:
                pass
        else:
            print(f"Could not load {font}, falling back to 'Times-Roman'")
            font = "Times-Roman"

    # load mappings
    tsv_mappings = json.load(open(args.mappings, "r"))

    # load tsv file and print each label
    with open(args.input, newline='') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t', quotechar='"')
        count = 0
        header = None
        total = 0
        for row in reader:
            if not header:
                header = []
                for s in row:
                    s = s.lower().replace(" ", "")
                    header.append(tsv_mappings.get(s, s))
                continue

            address = get_address(header, row)
            if address:
                address = format_address(address, countries, args.country)
            if address:
                print_label(canvas, font, fontsizes, padding, address, label, count, args.drawbox)
                count += 1
                total += 1
            if count >= label["across"] * label["down"]:
                canvas.showPage()
                count = 0

    print(f"Total {total} labels, on {canvas.getPageNumber()} pages.")

    # Save the PDF file
    canvas.save()


if __name__ == "__main__":
    main()
