# Server CPU Isolation Setup and Reversion for Experiments

This document outlines the steps to configure specific CPU cores on the experiment server for isolated (low-interference) execution of performance-sensitive tests, and how to revert these changes.

**Target Server CPU Topology (Example - 12th Gen Intel Core i5-12400F):**
*   Total Logical CPUs: 12 (0-11)
*   Physical Cores: 6
*   Hyper-Threading/SMT: Active (2 threads per core)
*   Pairings: (0,1), (2,3), (4,5), (6,7), (8,9), (10,11)

**Goal:** Isolate Physical Core 5 (Logical CPUs 10 and 11) for dedicated experimental use, minimizing OS scheduler and kernel interference.

## I. Setup Protocol for CPU Isolation

1.  **Connect to Server:**
    ```bash
    ssh your_username@your_remote_server
    ```

2.  **Verify Current CPU Topology (Optional but Recommended):**
    ```bash
    lscpu -e=CPU,CORE,SOCKET,NODE
    # Confirm pairings, e.g., CPUs 10 & 11 are siblings on the same physical core.
    ```

3.  **Backup GRUB Configuration (Recommended):**
    ```bash
    sudo cp /etc/default/grub /etc/default/grub.backup_$(date +%Y%m%d)
    echo "Backed up /etc/default/grub to /etc/default/grub.backup_$(date +%Y%m%d)"
    ```

4.  **Edit GRUB Configuration File:**
    Open `/etc/default/grub` with a text editor using sudo:
    ```bash
    sudo nano /etc/default/grub
    ```
    Or `sudo vim /etc/default/grub`, etc.

5.  **Modify `GRUB_CMDLINE_LINUX_DEFAULT`:**
    *   Locate the line starting with `GRUB_CMDLINE_LINUX_DEFAULT=`. It might look like:
        `GRUB_CMDLINE_LINUX_DEFAULT="quiet"`
    *   Append the isolation parameters to this line, within the quotes. For isolating CPUs 10 and 11, it should become:
        `GRUB_CMDLINE_LINUX_DEFAULT="quiet isolcpus=10,11 nohz_full=10,11 rcu_nocbs=10,11"`
        *(Ensure other existing parameters like "quiet" are preserved if they were there.)*

6.  **Save and Close the File.**

7.  **Update GRUB Bootloader Configuration:**
    ```bash
    sudo update-grub
    ```
    *(Note: On some systems like CentOS/RHEL, this might be `sudo grub2-mkconfig -o /boot/grub2/grub.cfg` or similar. `update-grub` is common for Debian/Ubuntu based systems.)*

8.  **Reboot the Server:**
    ```bash
    sudo reboot
    ```
    **Warning:** Ensure it's safe to reboot (no critical tasks running, other users informed if applicable).

9.  **Verify Isolation (After Reboot):**
    Connect via SSH again.
    ```bash
    cat /proc/cmdline
    ```
    The output should now include `isolcpus=10,11 nohz_full=10,11 rcu_nocbs=10,11`.
    When running experiments, use `taskset -c 10,11 your_command` to pin tasks to the isolated cores.

## II. Reversion Protocol (Back to Normal Scheduling)

1.  **Connect to Server:**
    ```bash
    ssh your_username@your_remote_server
    ```

2.  **Edit GRUB Configuration File:**
    ```bash
    sudo nano /etc/default/grub
    ```

3.  **Modify `GRUB_CMDLINE_LINUX_DEFAULT`:**
    *   Locate the line:
        `GRUB_CMDLINE_LINUX_DEFAULT="quiet isolcpus=10,11 nohz_full=10,11 rcu_nocbs=10,11"`
    *   Remove the added isolation parameters (`isolcpus=10,11 nohz_full=10,11 rcu_nocbs=10,11`).
    *   It should revert to its original state, e.g.:
        `GRUB_CMDLINE_LINUX_DEFAULT="quiet"`
        *(If you made a backup, you can compare against `cat /etc/default/grub.backup_YYYYMMDD` where YYYYMMDD is the date of backup).*

4.  **Save and Close the File.**

5.  **Update GRUB Bootloader Configuration:**
    ```bash
    sudo update-grub
    ```

6.  **Reboot the Server:**
    ```bash
    sudo reboot
    ```

7.  **Verify Reversion (After Reboot):**
    Connect via SSH again.
    ```bash
    cat /proc/cmdline
    ```
    The output should **no longer** include `isolcpus=10,11`, `nohz_full=10,11`, or `rcu_nocbs=10,11`. All CPUs should be available for general scheduling.

This document provides a clear reference for these operations. 