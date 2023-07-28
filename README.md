# Mlsync
> Kernel Repository Management Script

This Python script automates the process of cloning and updating git repositories from the [Kernel.org](https://lore.kernel.org). It scrapes Kernel.org for git repositories, clones them if they don't exist locally, and pulls the latest changes if they do.

## Features

- **Mirror Link Retrieval**: The script automatically finds the mirror link for each repository on Kernel.org.
- **Git Repository Cloning**: The script clones new git repositories found on Kernel.org.
- **Git Repository Updating**: The script updates (pulls the latest changes from) existing cloned repositories.
- **Git Repository Tracking**: The script keeps track of the repositories it has cloned, so it only updates those and clones new ones.

## Usage

Run the `git_clone_kernel()` function to start the script. This function will scrape Kernel.org for git repositories, clone new repositories, and update existing ones.

## Dependencies

This script requires Python 3 and the following libraries:

- `bs4 (BeautifulSoup)`
- `requests`

Ensure that these are installed in your Python environment before running the script. You can install them using pip:

```bash
pip install beautifulsoup4 requests
```
## Installation

1. To activate the venv, run the appropriate command based on your operating system:
- On macOS and Linux:

```bash
source venv/bin/activate
```
- On Windows:

```bash
venv\Scripts\activate
```

2. Tunning `python setup.py develop` provides you with a seamless way to utilize and engage with an actively developed Python project.

```bash
python setup.py develop
```

3. The adapter.py file should be executed. I will try to demonstrate how it can be done.
- The location of the adapter.py file needs to be found.

- If we consider that we want to store data in a file named "Kernel," we have reached the final stage of creating the "Kernel" file and entering it, to execute our adapter.py file.
> For example:

```bash
mkdir Kernel
cd Kernel
```
- If it has already been created, you can directly enter the file using the following command.
> For example:

```bash
cd Kernel
```

- Here, the command .../adapter.py should be written. The "..." should be replaced with the full path of the adapter.py file that we found in the first step.

> For example:

```bash
python /Users/burak/src/mlsync/mlsync/adapter.py
```

*At this stage, it is necessary for us to observe that the download and update processes have already been started.*

## Limitations

- This script does not handle cases where the local git repository has uncommitted changes. Before running the script, ensure that all changes in your local repositories have been committed or stashed, or they may be overwritten.

- On rare occasions, during the initial download of the archive, there may be instances where some archive downloads are skipped. This gap can be manually filled, but the program is already configured to handle the download of any new archive or archives, so the missing archive can also be downloaded by consecutively running the program. As mentioned, the archive deficiency is an uncommonly expected situation, but it is still advisable to compare the number of downloaded archive folders with the number of archives on lore.kernel.org

- In rare cases, file omissions may occur during the file updates. In such cases, the files that have not been updated will be printed to the screen. However, the files can also be manually updated if necessary, but as the program is capable of performing the updates, they can be updated by running the program.

## Disclaimer

This script is intended for educational purposes. Before using it to clone or pull from git repositories, ensure that you have the necessary permissions and that you are not violating any terms of service.

