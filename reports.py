from neuron import h
import os

recordlist = []
def voltage_record(gids):
    global voltage, time
    try: 
        os.mkdir("voltage_reports")
    except:
        pass
    pc = h.ParallelContext()
    time = h.Vector().record(h._ref_t)
    for gid in gids:
        flag = pc.gid_exists(gid)
        if flag > 0 :
            filename = 'voltage_reports/voltage_report_gid_%d.txt'%gid
            cell = pc.gid2cell(gid)
            voltage = h.Vector()
            voltage.record(cell.soma[0](0.5)._ref_v)
            #voltage.label("soma %d" % (gid))
            recordlist.append((voltage, filename))
        else:
            pass

def save_voltage():
    for vmrec, filename in recordlist:
        f = open(filename, 'w')
        for j in range(int(vmrec.size())):
            f.write('%g %g\n'%(time.x[j], vmrec.x[j]))
        f.close()

spike_netcons = []
def spike_record():
    global spikevec,idvec,n_spkout_files,n_spkout_sort
    pc = h.ParallelContext()
    nhost = pc.nhost()
    h.load_file("spike2file.hoc")
    idvec = h.Vector()
    idvec.buffer_size(5000000)
    spikevec = h.Vector()
    spikevec.buffer_size(5000000)
    n_spkout_files = max(nhost/64, 1)
    n_spkout_sort = min(n_spkout_files*8, nhost)
    pc.spike_record(-1, spikevec, idvec)



def save_spikes():
     h.spike2file('test', spikevec, idvec, n_spkout_sort, n_spkout_files)
