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
## Step 2: Start the program
</br>
There have been a few changes with the program since the first version.</br>
Instead of creating a new csv file, it will append the newly found entries to the old csv file. If there is no csv file with the same name in the folder, then it will create a new one. 
</br></br>
To change the job position, location or the amount of max entries you need to change the array that can be found on line 120-123. Each of the four arrays will be run through. That means that the index of each of the arrays corresponds to the index of the others. Main is run with position[0], location[0], maxCards[0] & firstEntry[0], then with position[1], location[1], maxCards[1] & firstEntry[1]. 
</br></br>

`position`: [Array that contains the job title (web developer, chemist, data scientist, etc.]


</br>

`location`: [Array that contains the location of the job (New York, San Francisco, etc.). For now it only looks in the USA]
</br>

`maxCards:` [Array that contains numbers. From the position & job location with the same index, it will grab as many entires as the entry in maxCards (3 positions of web developers in New York, 8 positions of chemists in San Francisco f.e.)]
</br>

`firstEntry:` [Array which simply tells the program if it's the first entry. If there's already a CSV file put False for every entry. If there's none yet, just put True for the first entry and False for the rest. It decides if the header row will be appended or not.]

</br></br>
## The pre-cleanup </br>
For the pre-cleanup we needed to import re (regex).</br>
The code for it can be found on `line 50`. </br></br>
<u>So far we can clean:</u>
- new lines
- every url that ends with .com
- every url that ends with .org
- every e-mail address
- any url that starts with https
- any url that starts with www
- any year in the format y-m-d
- any year in the format d/m/y
- any number with 4 or more digits

