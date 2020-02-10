# Grid Sample Download Tool

Handy tool to download grid samples to local.

# To use
* Create new folder "run" for logs output
```
mkdir run
```
* Copy files in on_atint (or folder for other platform) to "run" and go to "run"
```
cp src/* run
cd run
```
* Then prepare folder for output logs
```
mkdir logs
```
* Replace the sample_list.txt with to sample list file you want to use in get_sample.sh
* Replace the second argument with the path for output directory
* Then run:
```
condor_submit job.submit
```
