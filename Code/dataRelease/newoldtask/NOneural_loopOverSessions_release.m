%
% For all sessions, run cell selection
%
% paramsInPreset : struct, if set overwrites defaults.if field does not exist, default is used
%
% totStats and cellStatsAll contain results over all processed sessions
%
%
function [totStats,cellStatsAll] = NOneural_loopOverSessions_release(allRecogSessionsToUse, NOsessions, basepath, analysisMode, paramsInPreset ) 
totStats=[];
cellStatsAll=[];

for j=1:length(allRecogSessionsToUse) 
    
    NOind = allRecogSessionsToUse(j);

    NOsessionRecog = NOsessions(NOind);
    
    % import external parameters
    paramsIn = [];
    paramsIn.onlyChannels = copyFieldIfExists( paramsInPreset, 'onlyChannels', 1:196 );
    paramsIn.onlyCells    = copyFieldIfExists( paramsInPreset, 'onlyCells', [] );
    paramsIn.plotAlways   = copyFieldIfExists( paramsInPreset, 'plotAlways', 0 );
    paramsIn.onlyAreas    = copyFieldIfExists( paramsInPreset, 'onlyAreas', [] );
    paramsIn.doPlot       = copyFieldIfExists( paramsInPreset, 'doPlot', [] );
    paramsIn.exportFig    = copyFieldIfExists( paramsInPreset, 'exportFig', [] );

    paramsIn.NOind = NOind;
    paramsIn.analysisMode = analysisMode;
    paramsIn.diagnosisCode = NOsessions(NOind).diagnosisCode;
    
    % prepare data for this session
    [paramsForRun, basedirData_forSession,basedirEvents_forSession,brainArea] = prepareData_forSession_release( basepath,  NOsessionRecog, paramsIn );
    
    % run analysis for all cells in this session
    allDataRecog = runForAllCellsInSession( basedirData_forSession,  brainArea, NOsessionRecog.sessionID, @NO_singleCellAnalysis_release, paramsForRun );

    % aggregate results across sessions for later analysis
    if isfield(allDataRecog,'allStats')
        totStats = [totStats; [ ones(size(allDataRecog.allStats,1),1)*NOind, allDataRecog.allStats]];  
    end
    if isfield(allDataRecog,'cellStats')
       for ii=1:length(allDataRecog.cellStats)
           allDataRecog.cellStats(ii).NOind=NOind;
       end
       cellStatsAll = [ cellStatsAll allDataRecog.cellStats ]; 
    end

end
