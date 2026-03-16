# BootXray

**Visualizing Concurrency, Dependencies, and Delays during Linux Boot**

Modern Linux boot is highly concurrent with drivers and services executing in parallel under complex dependency chains, interrupt-driven wakeups, and asynchronous workloads. On heterogeneous systems, even with the same code, boot behavior varies by CPU topology, making regressions hard to debug.

Existing tools provide limited insight. Kernel logs and journalctl are useful only when failures are explicitly reported, and the initcall_debug timelines show where time is spent but don't explain why. Tools like systemd-analyze and bootchart identify slow components but mask systemic issues like CPU starvation, lock contention, and missed parallelism. While ftrace offers low-level visibility, correlating threads/kworkers activity to respective driver's context is tough.

Drawing on years of hands-on kernel boot debugging experience, we present **BootXray**—a trace-driven observability framework that combines ftrace data with early boot kprobe events and post-processing for correlation. When visualized in Perfetto, this produces a systemic view of boot behavior which can uncover root causes invisible to traditional tools, enabling faster debugging of boot issues.

## Approach

Boot-critical milestones like initcalls and functions are enabled using ftrace and kprobes. Ftrace logs are captured at device boot time.

**Ftrace events:** `initcall:*`

**Kprobes:** `really_probe`, `platform_probe`, `platform_dma_configure`, `of_platform_bus_probe`, and `of_platform_populate`

This ftrace log is later post-processed for visualizing the whole system using Perfetto.

## Ftrace/Kprobe Events Enabled During Boot

A sample GRUB configuration file is already uploaded to this project.

### Using GRUB

The following command line parameters can be added to your GRUB configuration:

```bash
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
```

### Using Source Code Approach

The following command line parameter can be used if using the source code approach:

```bash
trace_event=sched:*,workqueue:*,initcall:*,power:cpu_frequency trace_buf_size=100M log_buf_len=16M kprobe_event=p:Preally_probe,really_probe,dev=+0(+0(%x0)):string,drv=+0(+0(%x1)):string;r:Rreally_probe,really_probe;p:Pplatform_probe,platform_probe,dev=+0(+0(%x0)):string;r:Rplatform_probe,platform_probe;p:Pplatform_dma_configure,platform_dma_configure,dev=+0(+0(%x0)):string;r:Rplatform_dma_configure,platform_dma_configure;p:Pof_platform_bus_probe,of_platform_bus_probe,root=+0(+0(%x0)):string,parent=+0(+0(%x2)):string;r:Rof_platform_bus_probe,of_platform_bus_probe;p:Pof_platform_populate,of_platform_populate,root=+0(+0(%x0)):string,parent=+0(+0(%x3)):string;r:Rof_platform_populate,of_platform_populate;
```

## Post-Processing

The captured ftrace logs need to be post-processed to generate a format suitable for visualization in Perfetto. A Python script (`parser.py`) is included in this project to perform this post-processing. The script correlates ftrace events, kprobe data, and timing information to create a comprehensive view of the boot process.

**Usage:**
```bash
python parser.py <ftrace_log_file>
```

The post-processed output can then be loaded into [Perfetto UI](https://ui.perfetto.dev/) for interactive visualization and analysis.

## Result

The visualization in Perfetto provides a comprehensive view of the boot process, showing:
- Concurrent driver initialization and dependencies
- CPU utilization and scheduling patterns
- Workqueue activity and kworker threads
- Timing relationships between different boot components
- Bottlenecks and opportunities for optimization

<img width="853" height="326" alt="BootXray Perfetto Visualization" src="https://github.com/user-attachments/assets/c9083885-4fc6-4ca6-8981-5050cccf0fec" />

## Sample Logs

Sample logs are provided in the `sample-logs/` directory for reference and testing purposes.

## License

See the [LICENSE](LICENSE) file for details.
