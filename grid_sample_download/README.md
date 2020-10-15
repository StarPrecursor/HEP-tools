# Grid Sample Download Tool

Handy tool to download grid samples to local.

# To use on atint
* Set up rucio environment properly
```bash
source ~daits/atScripts/ATLASrucio_setups.sh
```
* Create new folder "run" for logs output
```bash
mkdir run
```
* Copy files in on_atint (or folder for other platform) to "run" and go to "run"
```bash
cp on_atint/* run
cd run
```
* Then prepare folder for output logs
```bash
mkdir logs
```
* Replace the sample_list.txt with to sample list file you want to use in get_sample.sh
* Replace the second argument with the path for output directory
* Then run:
```bash
condor_submit job.submit
```
