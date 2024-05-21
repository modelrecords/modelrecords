import semantic_version as semver
import re
import os
import requests
import mimetypes
import PyPDF2


def is_semver(version):
    # Regex to validate Semantic Versioning
    semver_regex = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    
    # Match the version string against the regex
    return bool(re.match(semver_regex, version))

def get_latest_semver(folder_path):
    
    semver_regex = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    max_version = None

    # Iterate over all files in the given folder
    for filename in os.listdir(folder_path):
        file_version = filename.rsplit('-', 1)[-1].split('.yaml')[0]
        match = re.match(semver_regex, file_version)
        if match:
            # Extract the semver part and parse it
            current_version = semver.Version(file_version)
            if max_version is None or current_version > max_version:
                max_version = current_version

    # Return the maximum version found, or None if no valid semver files were found
    return str(max_version) if max_version else None


def download_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def detect_format(url, content):
    content_type = mimetypes.guess_type(url)
    if content_type[0]:
        return content_type[0].split('/')[1]
    else:
        return url.split('.')[-1].lower()


def content_extract_text(self, refs, ref_path):
        text_files = []
        
        for idx, url in enumerate(refs):
            content = download_url(url)
            if content:
                format = detect_format(url, content)
                file_path = None
                if format == 'pdf':
                    file_path = f'{ref_path}/{idx:03}.{format}'
                
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    reader = PyPDF2.PdfReader(file_path)
                    all_text = ''
                    for page in reader.pages:
                        all_text += page.extract_text()
                    
                    file_path = f'{file_path}.txt'
                    with open(file_path, 'w') as f:
                        f.writelines(all_text)
                elif format in ['html', 'htm']:    
                    file_path = f'{ref_path}/{idx:03}.{format}.txt'
                    with open(file_path, 'wb') as f:
                        f.write(content)
                elif format in ['md', 'txt']:
                    file_path = f'{ref_path}/{idx:03}.{format}.txt'
                    with open(file_path, 'wb') as f:
                        f.write(content)
                else:
                    print("Format could not be determined.")
                
                if file_path:
                    text_files.append(file_path)
        return text_files
