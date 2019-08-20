import target_io as ti
import target_driver
import numpy as np
import pandas as pd

path = "/Volumes/gct-jason/astri_onsky_archive/d2019-05-01_mrk501/Run12817_r0.tio"

reader = ti.EventFileReader(path)
packet_size = reader.GetPacketSize()
n_packets_per_event = reader.GetNPacketsPerEvent()
packet = target_driver.DataPacket()
wf = target_driver.Waveform()

d_list = []
iev = 10892
for ipack in range(n_packets_per_event):
    event_packet = reader.GetEventPacket(iev, ipack)
    packet.Assign(event_packet, packet_size)
    module = packet.GetSlotID()
    first_cell_id = packet.GetFirstCellId()
    stale = packet.GetStaleBit()
    tack = packet.GetTACKTime()
    n_waveforms = packet.GetNumberOfWaveforms()

    print(ipack, n_waveforms, packet.IsEmpty(), packet.IsFilled(), packet.IsValid())

    for iwav in range(n_waveforms):
        packet.AssociateWaveform(iwav, wf)
        asic = wf.GetASIC()
        channel = wf.GetChannel()

        d_list.append(dict(
            ipack=ipack,
            module=module,
            first_cell_id=first_cell_id,
            stale=stale,
            tack=tack,
            n_waveforms=n_waveforms,
            asic=asic,
            channel=channel,
        ))

df = pd.DataFrame(d_list)
print(iev, np.unique(df['first_cell_id']))