# FIXApp
HCP FSL FIX pipeline add-on to https://github.com/yeunkim/HCPPipelines/tree/icafix

## Pre-requisites ##
Need to have run the HCP-MPP (including MELODIC) on the data. The MELODIC output folder ($fmri.ica) must be located in the $subj/$subj_output/sub-$subj/MNINonLinear/Results/$fmri/
The files must be temporally filtered (high bandpass, usually 2000). If FIX features have not been extracted, it will be automatically extracted.

## Main Pipeline Functions ##
    
* **Classifying: Classify ICA components using a specific training dataset.**
  * Requirements:
    * an existing training dataset
    * text file containing subject IDs at each new line must be created.
  * Usage: 
    ```
    docker run -ti --rm -v /path/to/parent/directory/containing/subjs/:/data \ 
    $CMD $TrainingDataName /data -i subj.txt -fn $fmri.ica --thresh $threshold --stages classify
    ```
    where:
    * $CMD : Docker image name
    * $TrainingDataName : Name of training dataset that was generated from the training step (i.e. HCP_hp2000) [ ${TrainingDataName}.RData must be located in train_${TrainingDataName} within the parent directory ]
    * subj.txt : Text containing subject IDs at each new line
    * $fmri.ica : MELODIC ICA folder names
    * $threshold : Threshold value for classifying. Range 0-100 (typically 5-20). Default is 10. Higher values imposes stricter standards and classifies less components as good
  * Output:
    * fix4melview_${TrainingDataName}\_thr${threshold}.txt will be located in each of the ${fmri}.ica folders
    
* **Cleaning: Clean artefacts using fix4melview_${TrainingDataName}\_thr${threshold}.txt file**
  * Requirements:
    * Classifying step must be run prior to this step. Or the text files can be created manually.
    * text file containing subject IDs at each new line must be created.
  * Usage:
  ```
  docker run -ti --rm -v /path/to/parent/directory/containing/subjs/:/data \ 
  $CMD $TrainingDataName /data -i subj.txt -fn $fmri.ica --stages clean
  ```
    where:
    * $CMD : Docker image name
    * $TrainingDataName : Name of training dataset that was generated from the training step (i.e. HCP_hp2000) 
    * subj.txt : Text containing subject IDs at each new line
    * $fmri.ica : MELODIC ICA folder names
    * --aggressive : Option to apply aggressive (full variance) cleaning for FIX
    * --hp : Option to apply high pass filter (temporal highpass full-width (2\*sigma) in seconds). Default is 2000. -1 applies no filtering to motion confounds. 0 applies linear detrending only.
  * Output:
    * filtered_func_data_clean.nii.gz will be located in each $fmri.ica folder.
    
## Other Functions ##

* **Training: Perform training to generate a trained-weights file.**
  * Requirements: 
    * hand_labels_noise.txt file (containing a list of bad components [1, 2, ...] in the last line) must be in each $fmri.ica folder. 
    * text file containing subject IDs at each new line must be created. 
  * Usage:
    ```
    docker run -ti --rm -v /path/to/parent/directory/containing/subjs/:/data \ 
    $CMD $TrainingDataName /data -i subj.txt -fn $fmri.ica --stages train
    ```
    where:
    * $CMD : Docker image name
    * $TrainingDataName : Name of training dataset to be generated (i.e. HCP_hp2000)
    * subj.txt : Text containing subject IDs at each new line
    * $fmri.ica : MELODIC ICA folder names
  * Output: 
    * All outputs (including ${TrainingDataName}.RData, logs, ${TrainingDataName}\_LOO, test results) will be located in train_${TrainingDataName} (i.e. train_HCP_hp2000) within the parent directory
    * **LOO test is automatically performed
    
* **Accuracy Testing: Test the accuracy of an existing training dataset on a set of hand-labelled subjects**
  * Requirements:
    * an existing training dataset
    * hand_labels_noise.txt file (containing a list of bad components [1, 2, ...] in the last line) must be in each $fmri.ica folder.
    * text file containing subject IDs at each new line must be created. 
  * Usage:
    ```
    docker run -ti --rm -v /path/to/parent/directory/containing/subjs/:/data \ 
    $CMD $TrainingDataName /data -i subj.txt -fn $fmri.ica -o $output --stages test
    ```
    where:
    * $CMD : Docker image name
    * $TrainingDataName : Name of existing training dataset with full path
    * subj.txt : Text containing subject IDs at each new line
    * $fmri.ica : MELODIC ICA folder names
    * $output : Output folder where the test results will be stored
  * Output:
    * LOO-style results will be located in $output folder within the parent directory.
    
    
## Running FIX pipeline ##

* **The FIX pipeline will perform classifying, and cleaning**
  * Usage:
    ```
    docker run -ti --rm -v /path/to/parent/directory/containing/subjs/:/data \ 
    $CMD $TrainingDataName /data -i subj.txt -fn $fmri.ica 
    ```
    where:
    * $CMD : Docker image name
    * $TrainingDataName : Name of exiarinf training dataset (i.e. HCP_hp2000 that is located in $pdir/train_HCP_hp2000)
    * subj.txt : Text containing subject IDs at each new line
    * $fmri.ica : MELODIC ICA folder names
    * Any optional arguments from classifying or cleaning stages can be used
    
### Running multiple stages ##
* list the stage names delimited by space after --stage flag. For example:
  ```
  --stage train classify
  ```
  where the stages are delimited by space.

## To build Docker image ##
1. ``` git clone https://github.com/yeunkim/FIXApp.git ```
2. ``` cd FIXApp ```
3. ``` docker build -t fix . ```

## Convert to Singularity-compatible image ##
``` 
docker run -v /var/run/docker.sock:/var/run/docker.sock \
 -v /path/to/where/singularityImg/will/be/output/:/output \
 --priveleged -t --rm singularityware/docker2singularity \
 -m " /mount/points/to/be/added " \
 fix 
```
When mounting, make sure that your Singularity configuration file has MOUNT HOSTFS = yes.

### To run Singularity ###
Just call the Singularity-compatible image with the arguments. For example, to run the main pipeline:

```
$singularityImg $TrainingDataName /data -i subj.txt -fn $fmri.ica 
```
