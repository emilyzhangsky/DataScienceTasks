import pandas as pd
import re


# JobTitle column clean function, extract job title,remove specify symbol
def find_job_title(job):
    result = re.split('( - |- | -)', job)
    result = result[0]
    result = re.split('( \\( |\\()', result)
    result = result[0]

    # start = result.find('- ')
    # if start != -1:
    #     result = result[:start].strip()
    # start = result.find(' -')
    # if start != -1:
    #     result = result[:start].strip()
    #
    # start = result.find('(')
    # if start != -1:
    #     result = result[:start].strip()

    result = re.sub('( and | or |and/or)', '/', result)
    result = re.sub('(!)', '', result)
    result = re.sub('( & | &|& )', '/', result)
    result = re.sub('( / | /|/ )', '/', result)
    return result


# JobID column clean function, extract JobID from url link
def find_job_id(job):
    start = str(job).rfind('/')
    end = str(job).find('?')
    result = str(job)[start + 1: end]
    return result


# Location & Area Column clean function, split location & area, deduplicate data in field
def find_duplicate(duplicate):
    match = re.match(r'(.+?)\1+$', duplicate)
    if match:
        duplicate = match.group(1)
    return duplicate


# Extract area column form the specify column
def find_area(area):
    start = str(area).find('area:')
    if start == -1:
        result = 'N/A'
    result = str(area)[start + len('area') + 1:].strip()
    return find_duplicate(result)


# Extract location column form the specify column
def find_location(location):
    start = str(location).find('location:')
    if start == -1:
        start = 0
    else:
        start = len('location') + 1

    end = str(location).find('area:')
    if end == -1:
        end = len(location) + 1
    result = str(location)[start: end].strip()
    return find_duplicate(result)


# Extract post time form the specify column
def find_post_time(post_time):
    result = re.findall(r'\d+[a-z|A-Z]', post_time)
    if result:
        result = result[0] + ' ago'
    else:
        result = 'N/A'
    return result


# Extract salary form the specify column
def find_salary(salary):
    result = re.search('[$]+', salary)
    if result:
        result = salary
    else:
        result = 'N/A'
    return result


frame = pd.read_excel('D:\\01 DataScience\\Training\\DataScienceTasks\\NZSeek\\data\\NZ_Admin_JOBS.xlsx',
                      sheet_name='sheet1')
frame = frame.rename(
    columns={'字段1': 'JobTitle', '字段1_link': 'JobID', '字段2': 'CompanyName', '字段3': 'Location', '字段4': 'PostTime',
             '字段5': 'Salary'})

frame.dropna(how='all')  # remove the row which all the data is empty
frame = frame.fillna({'CompanyName': 'N/A'})
frame['JobTitle'] = frame['JobTitle'].apply(find_job_title)
frame['JobID'] = frame['JobID'].apply(find_job_id)
frame['Area'] = frame['Location'].apply(find_area)
frame['Location'] = frame['Location'].apply(find_location)
frame['PostTime'] = frame['PostTime'].apply(find_post_time)
frame['Salary'] = frame['Salary'].apply(find_salary)

frame = pd.DataFrame(frame, columns=['JobID', 'JobTitle', 'CompanyName', 'Location', 'Area', 'PostTime', 'Salary'])
frame = frame.sort_values(by=['JobID', 'PostTime'])
frame = frame.drop_duplicates(['JobID'], keep='first')
frame = frame.sort_values(by=['JobID'])
frame.to_excel('D:\\01 DataScience\\Training\\DataScienceTasks\\NZSeek\\data\\CleansedData.xlsx')

# Question 1:
# How can I write the processed data to excel without automatically created index column

# Question 2:
# How can I combine multiple duplicated rows?
