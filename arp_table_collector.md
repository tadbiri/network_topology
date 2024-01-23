
# Collecting ARP table of Routers and Switchs

## Overview

This script performs a scheduled collection of Address Resolution Protocol (ARP) information on multiple devices, creating CSV files for further analysis. It utilizes concurrent execution for efficiency.

## Table of Contents

1. [Description](#description)
2. [Functions](#functions)
3. [Dependencies](#dependencies)
4. [Usage](#usage)
5. [Error Handling](#error-handling)
6. [Contributing](#contributing)
7. [License](#license)

## Description

The script connects to network devices using SSH and retrieves ARP information, creating CSV files with relevant details such as IP address, MAC address, and VLAN information.

## Functions

### 1. `split_by_dot(s)`

- **Description**: Splits a string at the first occurrence of a dot and returns a pandas Series.

### 2. `split_by_Vlanif(s)`

- **Description**: Splits a string at the first occurrence of 'Vlanif' and returns a pandas Series.

### 3. `split_by_slash(s)`

- **Description**: Splits a string at the first occurrence of '/-' and returns a pandas Series.

### 4. `ipbb_schedule(i)`

- **Description**: Performs IPBB schedule to collect ARP information and create CSV files.
- **Parameters**:
  - `i`: IP address of the device.

## Dependencies

- [pandas](https://pandas.pydata.org/)
- [cfg.connector](#) (Refer to the connector documentation for details)
- [cfg.credential](#) (Credentials handling module)
- [os](https://docs.python.org/3/library/os.html)
- [time](https://docs.python.org/3/library/time.html)
- [re](https://docs.python.org/3/library/re.html)
- [datetime](https://docs.python.org/3/library/datetime.html)
- [shutil](https://docs.python.org/3/library/shutil.html)
- [io](https://docs.python.org/3/library/io.html)
- [numpy](https://numpy.org/)
- [schedule](https://schedule.readthedocs.io/en/stable/)
- [concurrent.futures.ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   ```

2. Navigate to the script directory:

   ```bash
   cd your-repo/script-directory
   ```

3. Execute the script:

   ```bash
   python3 your_script.py
   ```

## Error Handling

The script includes error handling for various scenarios, including connection errors, timeouts, and general unexpected errors. Specific error messages are printed, and appropriate actions are taken for each type of error.

## Contributing

Feel free to contribute by creating issues, providing feedback, or submitting pull requests.

## License

This script is licensed under the [MIT License](LICENSE).

---

Replace the placeholder URLs (`#`) with the actual URLs if you have external documentation for the `cfg.connector` module and `cfg.credential` module. Also, make sure to create a `LICENSE` file in your repository and replace the `[MIT License](LICENSE)` link accordingly.