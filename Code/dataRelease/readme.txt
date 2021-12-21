Readme for code accompanying new/old single-neuron MTL recordings data release
==============================================================================

Internal note: If you're using the Rutishauser Lab source tree do not use the functions in this directory. They are copies of the originals and might be outdated.

1. Introduction
This directory contains a simplified version of the analysis code for VS and MS cells recorded from the human MTL.
The primary purpose of this code is two-fold: to illustrate how to use the released dataset and to reproduce the basic results as a way to provide technical validation of the released dataset.

See Faraut et al. 2017, Scientific Data, for details of the data structures involved and Rutishauser et al. 2015 Nat Neurosci for details of the task and data analysis.

2. Code
Main file to run the analysis is NOneural_main_release.m. Adjust the first few lines first to adjust paths of where the data and the source code is stored.
Running this function automatically adds all required functions to the path (using NOneural_main_addpath.m).

defineNOsessions_release.m provides a list of all released sessions. This list is a struct, with the index equal to the "NOID" (New/Old Task ID) described in the paper.

Matlab R2015a version was used to generate this code. We tested this code on Windows, Linux, and Mac OS X.

3. Permission to reuse
We are giving everyone the permission to use and modify this code as they see fit, provided that you cite our data descriptor paper as acknowledgment.

4. Code description and usage hints
===================================

The script NOneural_main_release.m is the main function that calls all other functions. Running it reproduces the main behavioral and neural results that were previously published with a subset of this dataset (Rutishauser et al., 2015).
NOneural_main_release.m is split into several sections ("Cells"), each of which begins with a "%%". Below, we describe each of the sections separately.

==================================================================
SECTION 1: Set parameters. 

At the beginning of NOneural_main_release.m, there are two parameters that need to be adjusted manually by the user before the code can be run. 
These parameters are: codePath and basepathData. Assuming that you copied your data into "c:\RecogMemoryMTL\", these paths would be set to:

codePath = 'c:\RecogMemoryMTL\Code\dataRelease\';
basepathData ='c:\RecogMemoryMTL\Data\';

If you use Linux or Mac OS X: in the example below, the assumption is you copied your data into '/home/urut/RecogMemoryMTL/' (adjust this accordingly). Then set these two variables as following:
codePath = '/home/urut/RecogMemorMTL/Code/dataRelease/';
basepathData = '/home/urut/RecogMemorMTL/Data/';


==================================================================
SECTION 2:  Which sessions to process 

This section uses the function defineNOsession_release.m to produce the 2 following outputs:
1)	NOsessions: a list of the sessions that are part of the public release with details concerning the experiment (note that many sessions don't exist here because they belong to different experiments), in particular:
-	NOsessions.EXPERIMENTIDLearn and NOsessions.EXPERIMENTIDRecog (80, 81, 82, 83 or 84): the initial event code that was used to identify the learning or recognition phases of the task. 
-	NOsessions.variant  (1,2 or 3): the task variant, informative of what set of stimuli was used. Each of this variant refers to a stimuli folder ("newolddelay", "newolddelay2", "newolddealy3", respectively) located in the "Stimuli" folder.
-	NOsessions.diagnosisCode (0 to 8): a code indicating the location of epileptic focal point: 0) not localized, 1) Right Mesial Temporal, 2) Left Mesial Temporal, 3) Right Neocortical Temporal, 4) Left Neocortical Temporal, 5) Right Lateral Frontal, 6) Left Lateral Frontal, 7) Bilateral Independent Temporal, 8) Bilateral Independent Frontal, 9) Right Other, 10) Left Other.
The index "c" in NOsessions indicates session number and is referred as NOind in the rest of the code.

2)	NO_listOf_allUsable: enables the user to indicate which sessions he/she wants to analyze.

==================================================================
SECTION 3: Analyze and plot behavior

In this section, the function NO_behaviorSummary is used to produce a summary figure of the main behavioral results.


==================================================================
SECTION 4: Single-neuron analysis. Loops over all available sessions and cells and runs the single-cell analysis function NO_singleCellAnalysis_release.m for each cell.

The parameter "analysisMode" determines whether the analysis is run for the learning or recognition block. Note that MS cell analysis is only possible for the recognition block.

The parameters "doPlot" and "plotAlways" determine whether single-cell plots (rasters/PSTH) will be plotted when running the code.
By default doPlot=1 and plotAlways=0, which means only plots for significant cells will appear. For fast processing, turn this off.

In this section, the function NOneural_loopOverSessions_release creates 2 matrices:
1)	totStats (see NO_singleCellAnalysis_release): 1 line per cell
-	col. 1: NOind: session number
-	col. 2: channel number
-	col. 3: cell number in the channel (in case many cells were recorded from the same channel) 
-	col. 4: brainAreaOfCell:  1=Right Hippocampus, 2=Left Hippocampus, 3=Right Amygdala, 4=Left Amygdala
-	col. 5: pBaseline. P-value of the t-test comparing the spike count between the baseline and the stimulus periods (see NO_singleCellAnalysis_release function)
-	col. 6: pNewOld. P-value of the bootstrap test comparing the spike count between old and new trials (see NO_singleCellAnalysis_release function) 
-	col. 7: pCategory. P-value of the anova test comparing the spike count between stimuli categories (see NO_singleCellAnalysis_release function)
-	col. 8: neuronType. 0: novelty- signaling neuron (activity for new>old) and 1: familiarity-signaling neuron (activity for old>new)
-	col. 9: number of old trials used in this analysis
-	col.10: number of new trials used in this analysis
-	col.11: rate. Firing rate of this cell during this task (see NO_singleCellAnalysis_release function)

2)	cellStatsAll (see NO_singleCellAnalysis_release): 1 line per cell
-	"channel": channel number
-	"cellNr: cell number in the channel (in case many cells were recorded from the same channel) 
-	"brainAreaOfCell":  1=Right Hippocampus, 2=Left Hippocampus, 3=Right Amygdala, 4=Left Amygdala
-	"origClusterID": original cluster name from the sorting
-	"timestamps": timing of each individual spike of this cell
-	"diagnosisCode"(0 to 8): a code indicating the location of epileptic focal point: 0) not localized, 1) Right Mesial Temporal, 2) Left Mesial Temporal, 3) Right Neocortical Temporal, 4) Left Neocortical Temporal, 5) Right Lateral Frontal, 6) Left Lateral Frontal, 7) Bilateral Independent Temporal, 8) Bilateral Independent Frontal, 9) Right Other, 10) Left Other.
-	 "newOldRecogLabels": labels for Ground Truth (new or old) in the Recognition task (1= "old" stimulus, 0= "new" stimulus)
-	"stimuliCategories": labels for the stimuli categories
-	"stimuliRecog": original stimulus ID of each recognition trial
-	"countBaseline": spike count for the baseline period (1 sec pre-stimulus onset: from 0 to stim onset (stim onset is at 1sec))
-	countStimulus_long: spike count for the stimulus period (0.2 to 1.7 sec post-stimulus onset)
-	"neuronType": 0: novelty-signaling neuron (activity for new>old) and 1: familiarity-signaling neuron (activity for old>new)
-	"indsOldUse": indexes of trials that have been used as "old" trials in the analysis.
-	"indsNewUse": indexes of trials that have been used as "new trials in the analysis.
-	"pVals": [pBaseline, pNewOld, pCategory] (see description above)
-	"rate": (see description above) Firing rate of this cell during this task.
-	"periods": timing for Learning or Recognition period
-	"NOind": session number

==================================================================
SECTION 5: summary stats across all neurons

This section provides a quantification of the different classified cells across all processed sessions.

==================================================================
SECTION 6:  Epileptic sites inclusions/exclusion 

This section enables the user to exclude or only include neurons from the epileptic sites from the totStats and cellStatsAll matrices. This is of interest to compare
effects of epilepsy on VS/MS neurons.

==================================================================
SECTION 7:  ROC stats. This reproduces basic aspects of the "high vs low" confidence ROC analysis shown in the Rutishauser et al 2015 paper.

The NO_selectSigCells_simple function produces a list of cells that satisfy certain criteria decided by the user. 
-	sigCellListMS: a list of the Memory selective cells
-	sigCellListVS: a list of the Visual selective cells
-	sigCellListVisResp: a list of the cells with a significant change of activity during the stimulus period compared to the baseline period.
-	sigCellList_valid: a list of all the above cells.

The NO_popAnalysis_ROC_plot_simple function produces the main previously published figures.


