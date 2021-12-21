%
%loads ROC data and calculates summary measures for later plotting
%id1-> same day; id2 -> overnight.
%
%
%urut/april08
function [typeCountersSame, typeCountersOvernight, bSame, bOvernight, daSame, daOvernight, RsquareSame, RsquareOvernight, percError, percCorrect, errorRateLearn,...
    RTsRecog, RTsLearn,percAccuracy_high, percAccuracy_low, responses_sameDay, recogState_sameDay,RTsRecog_vsQonset,StimOff_toQ_delay, ...
    StimOn_toOff_delay] = NObehaviorROC_prepare(NOsessions, id1, id2, doPlot, basepath, modeExcludeSlowRT )
if nargin<5
    basepath='/data/';
end
if nargin<6
    modeExcludeSlowRT=0;
end

sameDaySession = NOsessions(id1);
overnightSession = [];
if id2>0
    overnightSession = NOsessions(id2);
end

[FPOld,TPOld, FPNew,TPNew, typeCountersSame, percError, percCorrect, errorRateLearn,  RTsRecog, RTsLearn,percAccuracy_high, percAccuracy_low,responses_sameDay, ...
    recogState_sameDay, RTsRecog_vsQonset, StimOff_toQ_delay,StimOn_toOff_delay] = NObehaviorROC(sameDaySession, [], doPlot, basepath, modeExcludeSlowRT);

if id2>0
    [FPOld,TPOld, FPNew,TPNew, typeCountersOvernight] = NObehaviorROC( overnightSession, sameDaySession, doPlot,basepath);
    [bOvernight, d2, s, daOvernight, RsquareOvernight] = calcZROCSlope( typeCountersOvernight );
else
    typeCountersOvernight=[];
    bOvernight=[0 0];
    daOvernight=[0 0];
    RsquareOvernight=0;
end
[bSame, d2, s, daSame, RsquareSame] = calcZROCSlope( typeCountersSame );

