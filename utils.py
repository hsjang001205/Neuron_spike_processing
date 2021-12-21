import glob
import os.path
import scipy.io as io
import numpy as np
import pandas as pd
from scipy.stats import iqr
os.path.abspath("C:/Users/hsjang/Neuron/Neuron_spike_processing")

def add_line_v1(session, base_dir1, base_dir2):
    session = session.replace("\'", "")

    brain_area = io.loadmat(base_dir2+session+"/NO/brainArea.mat")
    brain_area = brain_area['brainArea']
    
    file_list = glob.glob(base_dir1+session+ "/NO/*.mat")
    neuron_reaction = None
    
    # Solving Spikes
    for f in file_list:
        mat_file = io.loadmat(f)
        temporal_spike = mat_file['spikes']
        spikes_list = list(set(temporal_spike[:,1]))

        n_cls = len(spikes_list)
        temporal_spikes_matrix = np.zeros((n_cls,2000), dtype = np.float32)

        for e, i in enumerate(spikes_list):
            temporal_spikes_matrix[e,0] = i
            for e2, i2 in enumerate(brain_area[:,2]):
                if i2 == i:
                    temporal_spikes_matrix[e, 1] = str(brain_area[e2, 3])

        for i in range(temporal_spike.shape[0]):
            for e2, j in enumerate(temporal_spikes_matrix[:,0]):
                if temporal_spike[i,1] == j:
                    temporal_spikes_matrix[e2,2+int((temporal_spike[i,2]-temporal_spike[0,2])/1000000)] += 1#(34-events_series[e])**2#
        if neuron_reaction is None:
            neuron_reaction = temporal_spikes_matrix

        else:
            neuron_reaction = np.concatenate([neuron_reaction,temporal_spikes_matrix], axis = 0)
    return neuron_reaction


def read_preset_for_avg():        
    d = {}
    neuron_reaction = None
    averages = None
    indicies = None
    base_dir1 = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Data_set/Data/sorted/"
    base_dir2 = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Data_set/Data/events/"
    with open("summarized.txt") as f:
        temporal = dict()
        for line in f:
            try:
                (key, val) = line.split("=")
                val = val.replace(" ", "").replace("\n", "")[:-1]
                if key == "NOsessions(c).session":
                    temporal['sec'] = val
                if key == "NOsessions(c).variant" and  val == "3":
                    if neuron_reaction is None:
                        neuron_reaction= add_line_v1(temporal['sec'],base_dir1,base_dir2)
                    else:
                        nr = add_line_v1(temporal['sec'],base_dir1,base_dir2)
                        neuron_reaction = np.concatenate([neuron_reaction, nr], axis = 0)
            except:
                continue
                
    return neuron_reaction
    
   



def add_line_v2(session, base_dir1, base_dir2, mem = False):
    session = session.replace("\'", "")
    # Solving Events
    mat_file = io.loadmat(base_dir2+session+"/NO/eventsRaw.mat")
    events = mat_file['events']
    brain_area = io.loadmat(base_dir2+session+"/NO/brainArea.mat")
    brain_area = brain_area['brainArea']
    time_series = []
    events_series = []
    time_start = 0
    time_end = 0
    start_time = 0
    end_time = 0
    for i in range(events.shape[0]):
        if (events[i,1] == 99 or events[i,1] == 55) and events[i+4,1] < 30 and not mem:
            start_time = events[i,0]
        if (events[i,1] == 99 or events[i,1] == 55) and events[i+4,1] >= 30 and mem:
            start_time = events[i,0]
        if events[i,1] == 1:
            time_start = events[i,0]
        if events[i,1] == 6: 
            if events[i-1,1] >= 30:
                continue
            events_series.append(events[i-1,1])
            time_end = events[i,0]
            time_series.append([time_start, time_end])
        
        if events[i,1] == 66 and events[i-2,1] < 30 and not mem:
            end_time = events[i,0]
        if events[i,1] == 66 and events[i-2,1] >= 30 and mem:
            end_time = events[i,0]

            
    if (len(time_series)) != 100:
        return k

    if ((end_time-start_time)/2000000) > 1000:
        return 0
    
    file_list = glob.glob(base_dir1+session+ "/NO/*.mat")
    neuron_reaction, averages, indicies, std = None, None, None, None
    
    # Solving Spikes
    for f in file_list:
        mat_file = io.loadmat(f)
        temporal_spike = mat_file['spikes']
        spikes_list = list(set(temporal_spike[:,1]))

        n_cls = len(spikes_list)
        temporal_spikes_matrix = np.zeros((n_cls,103), dtype = np.object)
        
        for e, i in enumerate(spikes_list):
            temporal_spikes_matrix[e,0] = session
            temporal_spikes_matrix[e,1] = i
            for e2, i2 in enumerate(brain_area[:,2]):
                if i2 == i:
                    temporal_spikes_matrix[e, 2] = str(brain_area[e2, 3])
        
        temporal_spikes_matrix = temporal_spikes_matrix[temporal_spikes_matrix[:,2] != 0]
        
        for i in range(n_cls):
            for j in range(3,103):
                temporal_spikes_matrix[i,j] = []
         
        
        average_spikes = np.zeros((n_cls), dtype = np.float32)
        indicies_sub = np.zeros((n_cls,103), dtype = np.int)
        
        for i in range(temporal_spike.shape[0]):
            time_indc = temporal_spike[i,2]
            for e2, j in enumerate(temporal_spikes_matrix[:,1]):
                if temporal_spike[i,1] == j:
                    if temporal_spike[i,2] >= start_time and temporal_spike[i,2] <= end_time:
                        average_spikes[e2] += 1
                        for e, t_pair in enumerate(time_series):
                            if time_indc < t_pair[1] and t_pair[0] < time_indc: 
                                indicies_sub[e2,e+3] = events_series[e]
                                if (temporal_spikes_matrix[e2,2] == '2' or temporal_spikes_matrix[e2,2] == '1') and (time_indc - t_pair[0])/1000 >= 0 and (time_indc - t_pair[0])/1000 <= 1800:
                                    temporal_spikes_matrix[e2,e+3].append((time_indc - t_pair[0])/1000)#(34-events_series[e])**2#
                                if (temporal_spikes_matrix[e2,2] == '3' or temporal_spikes_matrix[e2,2] == '4') and (time_indc - t_pair[0])/1000 >= 200 and (time_indc - t_pair[0])/1000 <=2000:
                                    temporal_spikes_matrix[e2,e+3].append((time_indc - t_pair[0])/1000)#(34-events_series[e])**2#
        times = 1000/((end_time-start_time)/1000)
        average_spikes = average_spikes * times
        
        std_spikes_arr = np.zeros((n_cls,int((end_time-start_time)/1800000) + 1), dtype = np.float32)
        for i in range(temporal_spike.shape[0]):
            for e2, j in enumerate(temporal_spikes_matrix[:,1]):
                if temporal_spike[i,1] == j and temporal_spike[i,2] >= start_time and temporal_spike[i,2] <= end_time:
                    std_spikes_arr[e2,int((temporal_spike[i,2]-start_time)/1800000)] += 1        
        
        #std_spikes = np.mean((std_spikes_arr-average_spikes.reshape(-1,1))**2, axis = 1)**0.5
        std_spikes = iqr(std_spikes_arr, axis = 1)
        average_spikes = np.median(std_spikes_arr, axis = 1)
        #print(std_spikes)
        #print(average_spikes)
        del std_spikes_arr
        
        
        if neuron_reaction is None:
            neuron_reaction = temporal_spikes_matrix
            averages = average_spikes
            indicies = indicies_sub
            std = std_spikes
        else:
            neuron_reaction = np.concatenate([neuron_reaction,temporal_spikes_matrix], axis = 0)
            averages = np.concatenate([averages,average_spikes], axis = 0)
            indicies = np.concatenate([indicies,indicies_sub], axis = 0)
            std = np.concatenate([std,std_spikes], axis = 0)
    return neuron_reaction, averages, std, indicies


def read_preset_recog(stimuli_mode = False):        
    d = {}
    neuron_reaction = None
    averages = None
    indicies = None
    std = None
    base_dir1 = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Data_set/Data/sorted/"
    base_dir2 = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Data_set/Data/events/"
    with open("summarized.txt") as f:
        temporal = dict()
        for line in f:
            try:
                (key, val) = line.split("=")
                val = val.replace(" ", "").replace("\n", "")[:-1]
                if key == "NOsessions(c).session":
                    temporal['sec'] = val
                if key == "NOsessions(c).variant" and  val == "3":
                    if neuron_reaction is None:
                        neuron_reaction, averages, std, indicies = add_line_v2(temporal['sec'],base_dir1,base_dir2)
                    else:
                        nr, av, st, ic = add_line_v2(temporal['sec'],base_dir1,base_dir2)
                        neuron_reaction = np.concatenate([neuron_reaction, nr], axis = 0)
                        averages = np.concatenate([averages,av], axis = 0)
                        indicies = np.concatenate([indicies, ic], axis = 0)
                        std = np.concatenate([std, st], axis = 0)
            except:
                continue
                
    dirs = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Code/dataRelease/stimFiles/newOldDelayStimuli3.mat"
    mat_file = io.loadmat(dirs)
    ctM = mat_file['categoryMapping'][:,0:2]
    dic_ = dict()
    for i in range(ctM.shape[0]):
        dic_[ctM[i,0]] = ctM[i,1]
    
    
    dirs = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Code/dataRelease/stimFiles/newOldDelay3_v3.mat"
    mat_file = io.loadmat(dirs)
    f1 = mat_file['experimentStimuli'][0][0][2][0]
    
    for i in range(len(f1)): 
        f1[i] = dic_[f1[i]]
    stimulus_type = f1.reshape(-1,1)
        
                                             
    neuron_reaction = neuron_reaction[std >0]
    averages = averages[std >0]
    indicies = indicies[std>0]
    std = std[std > 0]
    
    neuron_reaction_m = np.zeros(neuron_reaction.shape, dtype = np.object)
    neuron_reaction_m[:, :3] = neuron_reaction[:, :3]
    for i in range(neuron_reaction_m.shape[0]):
        for j in range(neuron_reaction_m.shape[1]-3):
            neuron_reaction_m[i,3+j] = (len(neuron_reaction[i,3+j])-averages[i])/std[i]
                
    if stimuli_mode:
        mat_file = io.loadmat(dirs)
        return neuron_reaction, neuron_reaction_m, mat_file['experimentStimuli'][0][0][2][0], averages, indicies
    else:
        return neuron_reaction, neuron_reaction_m, stimulus_type, averages, indicies


def add_line_v3(session, base_dir1, base_dir2,mem = True):
    session = session.replace("\'", "")

    # Solving Events
    mat_file = io.loadmat(base_dir2+session+"/NO/eventsRaw.mat")
    events = mat_file['events']
    brain_area = io.loadmat(base_dir2+session+"/NO/brainArea.mat")
    brain_area = brain_area['brainArea']
    time_series = []
    events_series = []
    time_start = 0
    time_end = 0
    start_time = 0
    end_time = 0
    for i in range(events.shape[0]):
        if (events[i,1] == 99 or events[i,1] == 55) and events[i+4,1] < 30 and not mem:
            start_time = events[i,0]
        if (events[i,1] == 99 or events[i,1] == 55) and events[i+4,1] >= 30 and mem:
            start_time = events[i,0]
        if events[i,1] == 1:
            time_start = events[i,0]
        if events[i,1] == 6: 
            if events[i-1,1] < 30:
                continue
            events_series.append(events[i-1,1])
            time_end = events[i,0]
            time_series.append([time_start, time_end])
        
        
        if events[i,1] == 66 and events[i-2,1] < 30 and not mem:
            end_time = events[i,0]
        if events[i,1] == 66 and events[i-2,1] >= 30 and mem:
            end_time = events[i,0]

            
    if (len(time_series)) != 100:
        return k
    
    
    if ((end_time-start_time)/2000000) > 1000:
        return 0
    
    file_list = glob.glob(base_dir1+session+ "/NO/*.mat")
    neuron_reaction, averages, indicies, std = None, None, None, None
    
    # Solving Spikes
    for f in file_list:
        mat_file = io.loadmat(f)
        temporal_spike = mat_file['spikes']
        spikes_list = list(set(temporal_spike[:,1]))

        n_cls = len(spikes_list)
        temporal_spikes_matrix = np.zeros((n_cls,103), dtype = np.object)
        
        for e, i in enumerate(spikes_list):
            temporal_spikes_matrix[e,0] = session
            temporal_spikes_matrix[e,1] = i
            for e2, i2 in enumerate(brain_area[:,2]):
                if i2 == i:
                    temporal_spikes_matrix[e, 2] = str(brain_area[e2, 3])
        
        #temporal_spikes_matrix = temporal_spikes_matrix[temporal_spikes_matrix[:,2] != 0]
        
        for i in range(n_cls):
            for j in range(3,103):
                temporal_spikes_matrix[i,j] = []
         
        
        average_spikes = np.zeros((n_cls), dtype = np.float32)
        indicies_sub = np.zeros((n_cls,103), dtype = np.int)
        
        for i in range(temporal_spike.shape[0]):
            time_indc = temporal_spike[i,2]
            for e2, j in enumerate(temporal_spikes_matrix[:,1]):
                if temporal_spike[i,1] == j:
                    if temporal_spike[i,2] >= start_time and temporal_spike[i,2] <= end_time:
                        average_spikes[e2] += 1
                        for e, t_pair in enumerate(time_series):
                            if time_indc < t_pair[1] and t_pair[0] < time_indc: 
                                indicies_sub[e2,e+3] = events_series[e]
                                if (temporal_spikes_matrix[e2,2] == '2' or temporal_spikes_matrix[e2,2] == '1') and (time_indc - t_pair[0])/1000 >= 0 and (time_indc - t_pair[0])/1000 <=2000:
                                    temporal_spikes_matrix[e2,e+3].append((time_indc - t_pair[0])/1000)#(34-events_series[e])**2#
                                if (temporal_spikes_matrix[e2,2] == '3' or temporal_spikes_matrix[e2,2] == '4') and (time_indc - t_pair[0])/1000 >= 300 and (time_indc - t_pair[0])/1000 <=2300:
                                    temporal_spikes_matrix[e2,e+3].append((time_indc - t_pair[0])/1000)#(34-events_series[e])**2#
        times = 2000/((end_time-start_time)/1000)
        average_spikes = average_spikes * times
        
        std_spikes_arr = np.zeros((n_cls,int((end_time-start_time)/2000000) + 1), dtype = np.float32)
        for i in range(temporal_spike.shape[0]):
            for e2, j in enumerate(temporal_spikes_matrix[:,1]):
                if temporal_spike[i,1] == j and temporal_spike[i,2] >= start_time and temporal_spike[i,2] <= end_time:
                    std_spikes_arr[e2,int((temporal_spike[i,2]-start_time)/2000000)] += 1        
        
        #std_spikes = np.mean((std_spikes_arr-average_spikes.reshape(-1,1))**2, axis = 1)**0.5
        std_spikes = iqr(std_spikes_arr, axis = 1)
        average_spikes = np.median(std_spikes_arr, axis = 1)
        #print(std_spikes)
        #print(average_spikes)
        del std_spikes_arr
        
        
        if neuron_reaction is None:
            neuron_reaction = temporal_spikes_matrix
            averages = average_spikes
            indicies = indicies_sub
            std = std_spikes
        else:
            neuron_reaction = np.concatenate([neuron_reaction,temporal_spikes_matrix], axis = 0)
            averages = np.concatenate([averages,average_spikes], axis = 0)
            indicies = np.concatenate([indicies,indicies_sub], axis = 0)
            std = np.concatenate([std,std_spikes], axis = 0)
    return neuron_reaction, averages, std, indicies


def read_preset_mem(stimuli_mode = False):        
    d = {}
    base_dir1 = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Data_set/Data/sorted/"
    base_dir2 = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Data_set/Data/events/"
    neuron_reaction = None
    averages = None
    indicies = None
    std = None
    with open("summarized.txt") as f:
        temporal = dict()
        for line in f:
            try:
                (key, val) = line.split("=")
                val = val.replace(" ", "").replace("\n", "")[:-1]
                if key == "NOsessions(c).session":
                    temporal['sec'] = val
                if key == "NOsessions(c).variant" and  val == "3":
                    if neuron_reaction is None:
                        neuron_reaction, averages, std, indicies = add_line_v3(temporal['sec'],base_dir1, base_dir2)
                    else:
                        nr, av, st, ic = add_line_v3(temporal['sec'],base_dir1, base_dir2)
                        neuron_reaction = np.concatenate([neuron_reaction, nr], axis = 0)
                        averages = np.concatenate([averages,av], axis = 0)
                        indicies = np.concatenate([indicies, ic], axis = 0)
                        std = np.concatenate([std, st], axis = 0)
            except:
                continue
                
    dirs = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Code/dataRelease/stimFiles/newOldDelayStimuli3.mat"
    mat_file = io.loadmat(dirs)
    ctM = mat_file['categoryMapping'][:,0:2]
    dic_ = dict()
    for i in range(ctM.shape[0]):
        dic_[ctM[i,0]] = ctM[i,1]
    
    
    #dirs = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Code/dataRelease/stimFiles/newOldDelay3_v3.mat"
    #mat_file = io.loadmat(dirs)
    #f1 = mat_file['experimentStimuli'][0][0][2][0]
    
    dirs = "C:/Users/hsjang/Neuron/Neuron_spike_processing/Code/dataRelease/stimFiles/newOldDelay3_v3.mat"
    mat_file = io.loadmat(dirs)
    f1 = mat_file['experimentStimuli'][0][1][3][0]
    f2 = mat_file['experimentStimuli'][0][1][4][0]
    
    for i in range(len(f1)): 
        f1[i] = dic_[f1[i]]
    stimulus_type = np.concatenate([f1.reshape(-1,1),f2.reshape(-1,1)], axis = 1)
         
    
    neuron_reaction = neuron_reaction[std >0]
    averages = averages[std >0]
    indicies = indicies[std>0]
    std = std[std > 0]
    
    neuron_reaction_m = np.zeros(neuron_reaction.shape, dtype = np.object)
    neuron_reaction_m[:, :3] = neuron_reaction[:, :3]
    for i in range(neuron_reaction_m.shape[0]):
        for j in range(neuron_reaction_m.shape[1]-3):
            neuron_reaction_m[i,3+j] = (len(neuron_reaction[i,3+j])-averages[i])/std[i]
                
    if stimuli_mode:
        mat_file = io.loadmat(dirs)
        return neuron_reaction, neuron_reaction_m, mat_file['experimentStimuli'][0][1][3][0], averages, indicies
    else:
        return neuron_reaction, neuron_reaction_m, stimulus_type, averages, indicies
    

def data_group_filter(df, gr_idx, value_idx):        
    idx = (df[value_idx] <= df.groupby(gr_idx)[value_idx].transform('quantile', 0.88)) & (df[1] >= df.groupby(gr_idx)[value_idx].transform('quantile', 0.1))
    df = df[idx]
    return df
