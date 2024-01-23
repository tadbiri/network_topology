
# Collecting ARP table of Routers and Switchs

## Overview

This Python script, written in Python 3.12, is designed to perform an IP Broadband (IPBB) schedule. The script connects to network devices, collects Address Resolution Protocol (ARP) information, and creates CSV files for further analysis. The script leverages multithreading for concurrent execution on multiple devices.

## Script Structure

The script is organized into distinct sections, each serving a specific purpose. 

### 1. Function Definitions

#### Splitting Functions
- **split_by_dot(s):**
  - Description: Splits a string at the first occurrence of a dot and returns a pandas Series.
- **split_by_Vlanif(s):**
  - Description: Splits a string at the first occurrence of 'Vlanif' and returns a pandas Series.
- **split_by_slash(s):**
  - Description: Splits a string at the first occurrence of '/-' and returns a pandas Series.

### 2. Main IPBB Schedule Function

#### ipbb_schedule(i)
- **Parameters:**
  - i: IP address of the device.
- **Description:**
  - Connects to a network device using the `connector` function.
  - Retrieves ARP information, MAC address, and hostname.
  - Processes and cleans the ARP data using pandas.
  - Handles connection-related errors, timeout errors, and other unexpected errors.
  - Creates CSV files with processed ARP information.
  - Executes the IPBB schedule concurrently on multiple devices using ThreadPoolExecutor.

### 3. Main Execution Block

- **if __name__ == "__main__":**
  - Sets up the script for execution.
  - Defines paths and initializes variables.
  - Copies the main IP list to a temporary file.
  - Retrieves a list of IP addresses from the credential module.
  - Uses ThreadPoolExecutor to concurrently execute the `ipbb_schedule` function on multiple devices.


### 4. Multithreading Explanation:

```python
with ThreadPoolExecutor(max_workers=200) as executor:
    ip_list = [i for i in ip_list]
    executor.map(ipbb_schedule, ip_list)
```

1. **ThreadPoolExecutor:**
   - The `ThreadPoolExecutor` is a concurrent executor that manages a pool of worker threads. It allows for the execution of functions concurrently in multiple threads.

2. **max_workers=200:**
   - It specifies the maximum number of worker threads in the pool. In this case, it's set to 200, meaning that up to 200 devices can be processed concurrently.

3. **ip_list = [i for i in ip_list]:**
   - This list comprehension ensures that the list of IP addresses (`ip_list`) is prepared for concurrent execution. It's a common practice to convert the iterable to a list before passing it to `executor.map`.

4. **executor.map(ipbb_schedule, ip_list):**
   - The `map` method of the `executor` takes two arguments:
     - The function to be executed concurrently (`ipbb_schedule` in this case).
     - The iterable of arguments to be passed to the function (`ip_list`).
   - The `map` method distributes the function calls across the available threads in the pool.

### Execution Flow:

- The `ThreadPoolExecutor` manages a pool of worker threads (up to the specified maximum) and processes each IP address concurrently.
- For each IP address, the `ipbb_schedule` function is invoked in a separate thread, allowing multiple devices to be processed simultaneously.
- The script benefits from the parallelism provided by multithreading, potentially reducing the overall execution time, especially when dealing with a large number of devices.

### Note:

- While multithreading can enhance concurrency, it's essential to be cautious with shared resources and ensure that the functions are thread-safe. In this script, the `ipbb_schedule` function seems to be designed to work independently for each IP address, which aligns well with multithreading.

## Usage

1. **Environment Setup:**
   - Ensure Python 3.12 or a compatible version is installed.
   - Install necessary dependencies by running:
     ```
     pip install pandas schedule
     ```

2. **Credential Configuration:**
   - Update the `cfg.credential` module with the necessary credentials.

3. **Execution:**
   - Run the script:
     ```
     python script_name.py
     ```

4. **Output:**
   - CSV files with processed ARP information are saved in the specified directory.


## Error Handling

- The script includes robust error handling for connection-related issues, timeout errors, and unexpected errors. Appropriate error messages are displayed for each scenario.
