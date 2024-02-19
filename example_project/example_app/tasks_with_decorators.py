from django_mlops.decorators import define_task

''' Task definitions for 'data_science_project1' using the renamed decorator '''
@define_task(process_name='data_science_project1', depends_on=[])
def fetch_data1():
    print("Fetching data 1")

@define_task(process_name='data_science_project1', depends_on=[])
def fetch_data2():
    print("Fetching data 2")
    data1 = fetch_service_data1()
    data2 = fetch_service_data2()
    return

def fetch_service_data1():
    service_data = call_api1()
    return service_data

def fetch_service_data2():
    return 'service_data1'

def call_api1():
    return 'api_call_data'

@define_task(process_name='data_science_project1', depends_on=['fetch_data1', 'fetch_data2'])
def clean_data():
    print("Cleaning data")

@define_task(process_name='data_science_project1', depends_on=['clean_data'])
def analyze_data():
    print("Analyzing data")

@define_task(process_name='data_science_project1', depends_on=['clean_data', 'analyze_data'])
def train_model():
    print("Training model")


''' Task definitions for 'web_scraping_project' using the renamed decorator'''

@define_task(process_name='web_scraping_project', depends_on=[])
def scrape_website():
    print("Scraping website")

@define_task(process_name='web_scraping_project', depends_on=['scrape_website'])
def extract_information():
    print("Extracting information")