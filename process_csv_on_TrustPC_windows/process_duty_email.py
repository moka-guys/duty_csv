"""
Process duty emails
Version 1.0.0
Developer: Igor Malashchuk 
Email: igor.malashchuk@nhs.net
Date Modified: 30/06/2022
"""
import subprocess
import os
import re
import collections
from datetime import datetime
import pandas

# run script: S:\Genetics_Data2\Array\Software\Python-3.6.5\python process_duty_email.py

def ask_for_folder():
    """
    For MokaPipe the destination folder can be different.
    Therefore this function ask the user to enter the last part of the folder
    """
    output_folder = ""
    #path_worksheets = "P:\\DNA LAB\\Current\\NGS worksheets\\"
    path_worksheets = "H:\\Tickets\\automate_end_of_duty_tasks\\Results\\"
    print("Part of destination is:{}".format(path_worksheets))
    while len(output_folder) == 0:
        output_folder = input(
            'Please complete the final part of the destination folder \n(e.g."NGS_401 to 500\\NGS484" place inside double quotes in PowerShell):'
        )
        print("The destination folder is : {}".format(path_worksheets + output_folder))
        choice = input('Is this correct ("Y"/"N" place insde double quotes in PowerShell):')
        if choice.capitalize() != "Y":
            output_folder = ""
    return path_worksheets + output_folder

def get_data(df, path_to_folder):
    """
    This function reads the data frame (df)..
    From the csv file it obtains the download links and uses a powershell script to download the links to the destination folder.
    """
    all_urls = ""
    for index, row in df.iterrows():
        line = row['url'] + "," + path_to_folder + " "
        all_urls += line
    return all_urls

def download_data(urls):
    process = subprocess.check_output(
            [
                "powershell.exe",
                "S:\\Genetics_Data2\\Array\\Software\\duty_bioinformatician_scripts\\get_DNAnexus_url.ps1",
                urls,
            ]
        )
    return process

def get_data_StG(df, path_to_folder):
    """
    This function reads the csv file.
    From the csv file it obtains the download links and uses a powershell script to download the links to the destination folder for StG transfer.
    """
    StG_urls = ""
    for index, row in df.iterrows():
        if bool(re.search("StG", row["url"])):  
            line = row['url'] + "," + path_to_folder + " "
            StG_urls += line
    return StG_urls

def save_log_file(text, filename): 
    cur_time = datetime.now()
    cur_time_string = cur_time.strftime("%Y_%m_%d__%H_%M_%S_")
    log_path =  "P:\\Bioinformatics\\Duty_Bioinformatics_CSV\\process_logs\\" + "Finished_on_{}_{}.txt".format(cur_time_string, filename)
    with open(log_path, 'w') as f:
        f.write(text)

def get_files():
    """
    This function gets the paths for csv files download by duty bioinformatician to the Duty_Bioinformatics_CSV folder.
    """
    folder = "P:\\Bioinformatics\\Duty_Bioinformatics_CSV"
    files = (
        file
        for file in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, file))
    )
    files_list = collections.defaultdict(list)
    #pattern = re.compile("__(\S+)__")
    for filename in files:
        results = re.search("__(\S+)__", filename)
        project = results.group(1)
        #project = pattern.search(filename)[1]
        filepath = folder + "\\" + filename
        files_list[project].append(filepath)
    files_merged = dict(files_list)
    return files_merged

class Project:
    """
    Process project
    """
    def __init__(self, project, files):
        self.project = project
        self.project_files = files
    def process_data(self):
        """
        This function executes the processing of a project based on the project type e.g. SNP, WES, TSO500 or MokaPipe
        """
        if self.project == "WES":
            Project.process_WES(self)
        elif self.project == "SNP":
            Project.process_SNP(self)
        elif self.project == "TSO500":
            Project.process_TSO(self)
        elif self.project == "MokaPipe":
            Project.process_MokaPipe(self)
    def process_WES(self):
        """
        Process WES Runs
        """
        #destination_of_files = "S:\\Genetics\\Bioinformatics\\NGS\\depthofcoverage\\genesummaries"
        destination_of_files = "H:\\Tickets\\automate_end_of_duty_tasks\\Results\\WES"
        for file_path in self.project_files:
            csv_file = pandas.read_csv(file_path, index_col=None)
            url_wes = get_data(csv_file, '"{}"'.format(destination_of_files))
            output = download_data(url_wes)
            list_of_stings = file_path.split("\\")
            save_log_file(output, list_of_stings[-1].replace('.csv',''))
            print(output)
    def process_SNP(self):
        """
        Process SNP Runs
        """
        destination_of_VCFs = "P:\\Bioinformatics\\VCFs_Andrew"
        for file_path in self.project_files:
            csv_file = pandas.read_csv(file_path, index_col=None)
            url_snp = get_data(csv_file, '"{}"'.format(destination_of_VCFs))
            output = download_data(url_snp)
            list_of_stings = file_path.split("\\")
            save_log_file(output, list_of_stings[-1].replace('.csv',''))
            print(output)
    def process_MokaPipe(self):
        """
        Process MokaPipe Runs
        """
        # Path to St George's transfer folder
        #StG_transfer = "P:\\DNA LAB\\StG SFTP\\StG SFTP outgoing"
        StG_transfer = 'H:\\Tickets\\automate_end_of_duty_tasks\\Results\\StG_outgoing'
        #pattern = re.compile("\\(NGS\S+)$")
        for file_path in self.project_files:
            # asks for final part to the destination folder
            output_folder = ask_for_folder()
             # create directory for RPKM and download data
            path_to_RPKM = output_folder + "\\RPKM"
            destination_of_Coverage = output_folder + "\\coverage"
            destination_of_FHPRS = output_folder + "\\FH_PRS"
            os.mkdir(path_to_RPKM)
            os.mkdir(destination_of_Coverage)
            os.mkdir(destination_of_FHPRS)
            # import csv file to pandas df
            csv_file = pandas.read_csv(file_path, index_col=None)
            # get data frames from the master df
            df_RPKM = csv_file[csv_file['type'] == 'RPKM']
            df_coverage = csv_file[csv_file['type'] == 'coverage']
            df_FHPRS = csv_file[csv_file['type'] == 'FH_PRS']
            # Create a folder with NGS run name, subfolders cold coverasge and RPKM, download data
            results = re.search(r"\\(NGS\S+)$", output_folder)
            foldername = results.group(1)
            StG_transfer_folder = StG_transfer + "\\" + foldername
            # Make directories in the outgoing folder
            os.mkdir(StG_transfer_folder)
            os.mkdir(StG_transfer_folder + "\\coverage")
            os.mkdir(StG_transfer_folder + "\\RPKM")
            os.mkdir(StG_transfer_folder + "\\FH_PRS")
            # Download data for StG Transfer
            url_RPKM = get_data(df_RPKM, '"{}"'.format(path_to_RPKM))
            url_coverage = get_data(df_coverage, '"{}"'.format(destination_of_Coverage))
            url_FHPRS = get_data(df_FHPRS, '"{}"'.format(destination_of_FHPRS))
            url_StG_RPKM = get_data(df_RPKM, '"{}"'.format(StG_transfer_folder + "\\RPKM"))
            url_StG_coverage = get_data_StG(df_coverage, '"{}"'.format(StG_transfer_folder + "\\coverage"))
            url_StG_FHPRS = get_data_StG(df_FHPRS, '"{}"'.format(StG_transfer_folder + "\\FH_PRS"))
            all_url =  url_RPKM + url_coverage + url_FHPRS + url_StG_RPKM + url_StG_coverage + url_StG_FHPRS
            output = download_data(all_url)
            list_of_stings = file_path.split("\\")
            save_log_file(output, list_of_stings[-1].replace('.csv',''))
            print(output)
    def process_TSO(self):
        """
        Process TSO500 Runs
        """
        # destination for the files to be downloaded to:
        destination_of_Results = 'H:\\Tickets\\automate_end_of_duty_tasks\\Results'
        #destination_of_Results = "P:\\Cancer_Genetics\\TSO500\\Results"
        # create folder woth project name
        for file_path in self.project_files:
            print(file_path)
            csv_file = pandas.read_csv(file_path, index_col=None)
            df_results = csv_file[csv_file['type'] == 'Results']
            df_coverage = csv_file[csv_file['type'] == 'coverage']
            df_sompy = csv_file[csv_file['type'] == 'sompy']
            search_results1 = re.search(r"_(TSO\d+).csv", file_path)
            search_results2 = re.search(r"002(_\S+)_TSO", file_path)
            folder_name = (
            search_results1.group(1) + search_results2.group(1)
            )
            path_to_folder = destination_of_Results + "\\" + folder_name
            # create subfolders called coverage and Results and download data:
            destination_of_Coverage = path_to_folder + "\\coverage"
            destination_of_extracted_Results = path_to_folder + "\\Results"
            destination_of_sompy = path_to_folder
            os.mkdir(path_to_folder)
            os.mkdir(destination_of_Coverage)
            os.mkdir(destination_of_extracted_Results)
            url_coverage = get_data(df_coverage, '"{}"'.format(destination_of_Coverage))
            url_sompy = get_data(df_sompy, '"{}"'.format(destination_of_sompy))
            url_results = get_data(df_results, '"{}"'.format(path_to_folder))
            all_url = url_coverage + url_sompy + url_results
            output = download_data(all_url)
            list_of_stings = file_path.split("\\")
            save_log_file(output, list_of_stings[-1].replace('.csv',''))
            print(output)
    def archive_files(self):
        """
        Modufy the csv file to remove data from it and insert a message of when it was compelted and by whome.
        """
        # get the user infromation and current date
        #user = os.getlogin() -> does not work when executing the script from PowerShell
        cur_time = datetime.now()
        cur_time_string = cur_time.strftime("%Y_%m_%d__%H_%M_%S_")
        # message to be added to the csv file
        message = "Processed_on_{}".format(
            cur_time_string
        )
        # Repalce data in csv file with the message and move the files to archive folder.
        for file_path in self.project_files:
            #subprocess.Popen("echo {} > {}".format(message, file_path))
            file_path_list = file_path.split("\\")
            new_name = message+file_path_list[3]
            print(new_name)
            file_path_list = file_path_list[:3] + ["archive"] + [new_name]
            archive_file_path = "\\".join(file_path_list)
            os.rename(file_path, archive_file_path)
        
if __name__ == "__main__":

    data = get_files()
    print(data)
    for key in data:
        project = Project(key, data[key])
        project.process_data()
        project.archive_files()
