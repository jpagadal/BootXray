# BootXray
Visualizing Concurrency, Dependencies, and Delays during Linux Boot

Modern Linux boot is highly concurrent with drivers and services executing in parallel under complex dependency chains, interrupt driven wakeups, and asynchronous workloads.  On heterogeneous systems, even with the same code, boot behavior varies by CPU topology, making regressions hard to debug.
 
Existing tools provide limited insight. Kernel logs and journalctl are useful only when failures are explicitly reported and the initcall_debug timelines show where time is spent, but doesn’t explain why.  Tools like systemd-analyze, bootchart identifies slow components but mask systemic issues like CPU starvation, lock contention, and missed parallelism. While ftrace offers low-level visibility, correlating threads/kworkers activity to respective driver’s context is tough.
 
Drawing on years of hands on kernel boot debugging experience, we present BootXray—a trace driven observability framework that combines ftrace data with early boot kprobe events and post processing for correlation. When visualized in Perfetto, this produces a systemic view of boot behavior which can uncover the root causes invisible to traditional tools, enabling faster debug of boot issues.

# Approach 
Boot critical milestones like initcalls & functions are enabled using ftrace and kprobes. Ftrace logs are captured at the device boot time.
Ftrace events: initcall:*
Kprobes: really_probe, platform_probe,platform_probe, platform_dma_configure, of_platform_bus_probe & of_platform_populate

This ftrace log is later post-processed for visualising the whole system using perfetto.

# Ftrace/kprobe events enabled during boot

Sample grub file is already uploaded to this project.
Following command line params can be used if using grub. 

GRUB_CMDLINE_LINUX_DEFAULT="trace_event=sched:*,workqueue:*,initcall:*,power:cpu_frequency trace_buf_size=100M log_buf_len=16M \
kprobe_event=\"\
p:Preally_probe,really_probe,dev=+0(+0(%x0)):string,drv=+0(+0(%x1)):string;\
r:Rreally_probe,really_probe;\
p:Pplatform_probe,platform_probe,dev=+0(+0(%x0)):string;\
r:Rplatform_probe,platform_probe;\
p:Pplatform_dma_configure,platform_dma_configure,dev=+0(+0(%x0)):string;\
r:Rplatform_dma_configure,platform_dma_configure;\
p:Pof_platform_bus_probe,of_platform_bus_probe,root=+0(+0(%x0)):string,parent=+0(+0(%x2)):string;\
r:Rof_platform_bus_probe,of_platform_bus_probe;\
p:Pof_platform_populate,of_platform_populate,root=+0(+0(%x0)):string,parent=+0(+0(%x3)):string;\
r:Rof_platform_populate,of_platform_populate;\
\""

Following cmdline param can be used if source code approach used.

\"trace_event=sched:*,workqueue:*,initcall:*,power:cpu_frequency trace_buf_size=100M log_buf_len=16M kprobe_event=p:Preally_probe,really_probe,dev=+0(+0(%x0)):string,drv=+0(+0(%x1)):string;r:Rreally_probe,really_probe;p:Pplatform_probe,platform_probe,dev=+0(+0(%x0)):string;r:Rplatform_probe,platform_probe;p:Pplatform_dma_configure,platform_dma_configure,dev=+0(+0(%x0)):string;r:Rplatform_dma_configure,platform_dma_configure;p:Pof_platform_bus_probe,of_platform_bus_probe,root=+0(+0(%x0)):string,parent=+0(+0(%x2)):string;r:Rof_platform_bus_probe,of_platform_bus_probe;p:Pof_platform_populate,of_platform_populate,root=+0(+0(%x0)):string,parent=+0(+0(%x3)):string;r:Rof_platform_populate,of_platform_populate;\"


# Post processing 

Post processing (python script - AI developed) uploaded to this project.

# Result 




