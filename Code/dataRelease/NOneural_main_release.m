%% Main file for new/old analysis (behavior and single-unit)
%==================================================================
% NOneural_main_release.m
%
% Code that demonstrates how to read and utilize the human single-unit MTL data acquired during the new/old recognition task.
% This code is part of the data, code, and description released as part of our 2017 data release (DOI http://dx.doi.org/10.5061/dryad.46st5 ). 
% 
% The two papers that describe this data are:
%
%Rutishauser, U., S. Ye, M. Koroma, O. Tudusciuc, I.B. Ross, J.M. Chung, and A.N. Mamelak. 
%Representation of retrieval confidence by single neurons in the human medial temporal lobe. 
%Nature Neuroscience, 2015. 18(7): p. 1041-50.
%
%Faraut, M.C.M., Carlson, A., Sullivan, S., Tudusciuc, O., Ross, I., Reed, C.M., Chung, J.M., Mamelak, A.N., Rutishauser, U.
%Dataset of human medial temporal lobe single neuron activity during declarative memory encoding and recognition.
%Scientific Data, in press (2017).
%
% Feel free to use this code and data for your own purposes. If you publish work based on this data/code, please cite our data descriptor.
%
% Rutishauser Lab, Cedars-Sinai/Caltech, August 2017.  http://www.rutishauserlab.org/
%==================================================================


%% Section 1: Set Parameters - modify this section before running this code !

% Point this directory to where the downloaded code is located.
codePath = 'Code/dataRelease/'; % => enter here your path where the code is located. For Windows: 'xxx\Code\dataRelease\'; For Linux or Mac: 'xxx/Code/dataRelease/', where 'xxx' is the directory that contains the location where you unzipped the downloaded data into.

% Point this directory to where the downloaded data is located. This directory should contain two sub-directories: sorted and events
basepathData = 'Data/';%  => enter here your path where the data is located. For Windows: 'xxx\Data\'; For Linux or Mac: 'xxx/Data/', where 'xxx' is the directory that contains the location where you unzipped the downloaded data into.

addpath(fullfile(codePath)); 
NOneural_main_addpath( codePath );

%% Section 2: Which sessions to process
[NOsessions,NO_listOf_allUsable] = defineNOsessions_release();

%List of sessions to analyze. For testing purposes, list only one or a few. To process all: set equal to NO_listOf_allUsable
%allSessionsToUse = [ 114 115 119 120 ]; 
%allSessionsToUse=NO_listOf_allUsable(end-20:end);
allSessionsToUse = NO_listOf_allUsable;   % process all available

%allSessionsToUse=98;

%% Section 3: Analyze and plot behavior
doPlot_behavior = 1;
modeBehavior = 1;  %0: fixed, 1: criterion threshold, 2: TP threshold. DEFAULT is 1
modeExcludeSlowRT = 0; %all trials (default); if one, slow RT trials are excluded to see if this effects results. 0 none, 1 strict (1sd, <5s), 2 lenient (3sd, <30s). See NObehaviorROC.m

%-- behavior summary figure (all sessions)
if length(allSessionsToUse)>1    % only works if at least two sessions are analyzed
   if  doPlot_behavior == 1
       figure(7);
   end
    decisionThresholds = NO_behaviorSummary(NOsessions, allSessionsToUse, modeBehavior, doPlot_behavior, basepathData, modeExcludeSlowRT);
end

%% Section 4: Single-neuron analysis. Loop over all available cells and run analysis on each independently
% which analysis to run.  1 is recognition/retrieval part (category/MS cells); 2 is learning part (VS cells only)
analysisMode = 1;    % recognition part. only this mode allows what follows to run (MS/VS cell analysis)
%analysisMode = 2;    % learning part. No MS cell analysis here since all images are novel at this point.

paramsInPreset=[];
paramsInPreset.doPlot = 1;   % plot significant units. Warning, doPlot=1 generates a lot of figures! Put doPlot=0 to avoid that: it will only run statistics but don't make plots.
paramsInPreset.plotAlways = 0; % if enabled, plot all cells regardless of significance
paramsInPreset.onlyChannels = [];   % to focus on particular set of channel(s), set this to a list of numbers. ie. [22 25 28].  [] means all channels available.
paramsInPreset.onlyAreas = [1 2 3 4 ];   % which areas to process. see translateArea.m 
paramsInPreset.exportFig = 0; % store figs as eps; check path in NO_singleCellAnalysis_release.m
[totStats,cellStatsAll] = NOneural_loopOverSessions_release(allSessionsToUse, NOsessions, basepathData,analysisMode, paramsInPreset ); 

%% Section 5: Summary stats across all neurons
alphaVal = 0.05;  %p-value cutoff used for a cell to count as significant

nrVsBaseline = length(find(totStats(:,5)<alphaVal));  %how many diff vs baseline
nrMS         = length(find(totStats(:,6)<alphaVal));  %how many VS cells
nrVS         = length(find(totStats(:,7)<alphaVal));  %how many MS cells
nrTot        = size(totStats,1);

disp(['#tot: ' num2str(nrTot) ' #MS:' num2str(nrMS) ' #VS:' num2str(nrVS)]);

%% Section 6: Epileptic sites exclusion 
epilepsyExclusionMode = 0;
    % epilepsyExclusionMode = 0; % no exclusion
    % epilepsyExclusionMode = 1; % only in non-epileptic temporal
    % epilepsyExclusionMode = 2; % only in non-epileptic side (strict)
    % epilepsyExclusionMode = 3; % only in epileptic temporal (strict)
    % epilepsyExclusionMode = 4; % only in epileptic side
    % epilepsyExclusionMode = 5; % only in non-epileptic temporal, include non-localized
if epilepsyExclusionMode>0                                                  
    [ListOfCellsToUse, cellStatsAll_exclusion,totStats_exclusion ] = EpilepticSitesExclusion(cellStatsAll, totStats, epilepsyExclusionMode);
    cellStatsAll = cellStatsAll_exclusion;totStats = totStats_exclusion;
end
    
%% Section 7: ROC stats. This reproduces basic aspects of the "high vs low" confidence ROC analysis shown in the Rutishauser et al 2015 paper.
% this can only be run if analysisMode==1
minRateToUse = 0 ;
alphaLimBootstrap = 0.05;
minNrTrials = 10; % require at least this many trials per condition; at least that many correct trials for both new & old are required
enforceBehaviorExclusions = 1; % 0 include all; 1 include all with valid behavior; 2 include only those that distinguished high/low correctly
areaToProcessList = 1:4; % all MTL
balanceNrTrials = 0; %if 1, use equal nr trials in both groups when calculating AUC
randomizeHighLow = 0; %if 1, control (scramble high/low)
bootstrapChanceLevels = 0;
highLowSplitDynamic = 0; %0 no, 1 yes
countWindow = [ 1200 2700];

% select cells that satisfy above criteria
[sigCellListMS, sigCellListVS, sigCellListVisResp, sigCellList_valid] = NO_selectSigCells_simple(areaToProcessList, totStats, minRateToUse, minNrTrials, cellStatsAll, enforceBehaviorExclusions, alphaLimBootstrap );

% plot ROC population stats of selected cells
NO_popAnalysis_ROC_plot_simple( cellStatsAll, sigCellListMS, bootstrapChanceLevels, randomizeHighLow, balanceNrTrials, highLowSplitDynamic, countWindow );
