This Script will gather data from Indeed

JobTitle, JobLocation,CompanyName,JobSummary,PostDate,Date of Extraction, Salary, JobURL, DescriptionText

start with
python ./main.py --position 'POSITION' --location 'LOCATION' --maxSize MAX_NUMBER_OF_JOBLISTINGS

this will save a csv file with the data

It will access data from the US Website of Indeed.(cause English Job Description are better for keyword processing)

Before running code do not fotget to install packages:
pip install requests
pip install bs4 




# Web Scraping with Python and Beautiful Soup
</br></br>
## Step 1: Installation
First of all you need to figure out which Python version you have installed on your device. On some machines Python 2.?.? is installed by default, which is not what we want here. The latest version of python that I am currently using is 3.7.3
</br></br>
### Installing Beautiful Soup on MacOS
`pip install bs4` - You need pip installed for this
### Installing requests on MacOS
`pip install requests`
</br></br>
### Known Errors:
I had an error saying that the libraries can't be imported. <b>Fix</b>:
1) Select Interpreter command from the Command Palette (Ctrl+Shift+P)

2) Search for "Select Interpreter"

3) Select the installed python directory (3.7.3 in my case)

</br></br></br>
## Step 2: Which elements of the Indeed page do we need?
- job title
- location
- company name
- salary
- description
- start date
- job type
- work role // what's that exactly again? If it's 'Senior' etc. then it's in the job name for now
</br>
We only have access to job title, location, company name, salary and description for now.

