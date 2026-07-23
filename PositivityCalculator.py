# Gives Positivity Scores to All Generated Groups (takes a input file)

import re 

groupTitle = ""
groupCount = 0
totalCount = 0

sentGroup = {"positive":0,"negative":0,"neutral":0,"total":0}
lineact = []

inputFile = input("Type File Name: ")

with open(inputFile, "r") as file:
	for line in file:
		if line == "\n":
			continue
		elif re.search(r"\[\[\*\* Group (\d) .+",line):
			sentTitle = re.search(r"\[\[\*\* Group (\d) .+",line)
			if sentTitle.group(1) == '0':
				groupTitle = sentTitle.group()
			else:
				avg = sentGroup["total"] / groupCount
				normalizedScore = (avg + 1) / 2
				lineact.append(f"{groupTitle}, Total comments in group: {groupCount}, Positivity Score: {normalizedScore:.3f}")
				sentGroup = {"positive":0,"negative":0,"neutral":0,"total":0}
				groupCount = 0 
				groupTitle = sentTitle.group(0)
		elif re.search(r':: (\w+)=(\d{1,2}\.\d{2}), (\w+)=(\d{1,2}\.\d{2}), (\w+)=(\d{1,2}\.\d{2})',line):
			sentiment = re.search(r':: (\w+)=(\d{1,2}\.\d{2}), (\w+)=(\d{1,2}\.\d{2}), (\w+)=(\d{1,2}\.\d{2})',line)
			sentGroup[sentiment.group(1)] = (float(sentiment.group(2)) / 100)
			sentGroup[sentiment.group(3)] = (float(sentiment.group(4)) / 100)
			sentGroup[sentiment.group(5)] = (float(sentiment.group(6)) / 100)
			currentLine = (sentGroup["positive"] * 1) + (sentGroup["negative"] * -1)
			sentGroup["total"] += currentLine
			groupCount +=1
			totalCount +=1
		if re.search(r'^Keywords: \w+,\w+',line):
			pass
	avg = sentGroup["total"] / groupCount
	normalizedScore = (avg + 1) / 2
	lineact.append(f"{groupTitle}, Total comments in group: {groupCount}, Positivity Score: {normalizedScore:.3f}")



with open("results.txt","w") as outputfile:
	for i in lineact:
		outputfile.write(i + '\n')
	outputfile.write(f"Total Comments: {totalCount}")






