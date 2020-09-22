# "Brazilian" plot tool

Makes brazilian plot with simple config file

## Usage

- Prepare configuration file for plotting  

   You can check example config file "example_limit.cfg"  
   There are 5 sections inside config file:
  - **INFO** general infomation
  - **INPUT** input data for plotting
  - **TREX** (alternative) specify outputs from TrexFitter to get limits from
  - **PLOT** plot options
  - **FILE** output format

- Run with Python

    ```bash
    python plot_brazilian.py example_limit.cfg
    ```