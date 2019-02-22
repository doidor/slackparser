import json
import sys
import re

from os import listdir
from os.path import isfile, join, splitext
from datetime import datetime
from pprint import pprint
from tabulate import tabulate
from textwrap import wrap
from lib import HTML

IMPORTS_DIR = './imports/'
EXPORTS_DIR = 'exports/'

EXPORTS_JSON = f'{EXPORTS_DIR}/conversation.json'
EXPORTS_TXT = f'{EXPORTS_DIR}/conversation.txt'
EXPORTS_HTML = f'{EXPORTS_DIR}/conversation.html'

HTML_TEMPLATE = 'conversation-template.html'


def replace_url_to_link(value):
    # Replace url to link
    urls = re.compile(
        r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE | re.UNICODE)
    value = urls.sub(r'<a href="\1" target="_blank">\1</a>', value)
    # Replace email to mailto
    urls = re.compile(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)",
                      re.MULTILINE | re.UNICODE)
    value = urls.sub(r'<a href="mailto:\1">\1</a>', value)
    return value

def parseJsons():
	fileNames = [splitext(f)[0] for f in listdir(
		IMPORTS_DIR) if isfile(join(IMPORTS_DIR, f))]

	fileNames.sort(key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

	jsonList = list()

	for f in fileNames:
		fileName = join(IMPORTS_DIR, f'{f}.json')

		with open(fileName) as jsonFile:
			data = list(json.load(jsonFile))
			jsonList += data

	return jsonList

def getTableData(jsonData, withLinks=False, wrapLines=True):
	conversations = []

	for entry in jsonData:
		username = entry.get("username", None) or entry.get("user", None)
		postDate = datetime.utcfromtimestamp(
			float(entry.get('ts'))).strftime('%Y-%m-%d %H:%M:%S')
		message = entry.get("text", None) or "Probably contains an attachment"

		if wrapLines:
			message = "\n".join(wrap(message))

		if withLinks:
			message = replace_url_to_link(message)

		conversations.append((postDate, username, message))

	return conversations

def exportAsJson(jsonData):
	with open(EXPORTS_JSON, 'w') as exportsJson:
		json.dump(jsonData, exportsJson)

def exportAsText(tableData):
	with open(EXPORTS_TXT, 'w') as exportsText:
		exportsText.write(tabulate(tableData, headers=[
		                  "Date", "Username", "Message"], tablefmt='grid'))

def exportAsHtml(jsonData):
	tableData = getTableData(jsonData, withLinks=True, wrapLines=False)

	with open(HTML_TEMPLATE) as htmlTemplate:
		with open(EXPORTS_HTML, 'w') as exportsHtml:
			htmlContent = htmlTemplate.read()

			htmlTable = HTML.table(tableData, header_row=[
                            "Date", "Username", "Message"])

			exportsHtml.write(htmlContent % {'BodyData': htmlTable})


if __name__ == '__main__':
	jsonData = parseJsons()
	tableData = getTableData(jsonData)

	exportAsJson(jsonData)
	print("Finished json export.")
	exportAsText(tableData)
	print("Finished text export.")
	exportAsHtml(jsonData)
	print("Finished html export.")





