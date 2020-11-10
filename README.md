This Script will gather data from Indeed

JobTitle, JobLocation,CompanyName,JobSummary,PostDate,Date of Extraction, Salary, JobURL, DescriptionText

start with
python ./main.py --position 'POSITION' --location 'LOCATION' --maxSize MAX_NUMBER_OF_JOBLISTINGS

this will save a csv file with the data

It will access data from the US Website of Indeed.(cause English Job Description are better for keyword processing)

Before running code do not fotget to install packages:
pip install requests
pip install bs4 
