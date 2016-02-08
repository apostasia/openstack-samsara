#!/bin/bash

sudo mkdir /sys/fs/cgroup/cpuacct
sudo mkdir /sys/fs/cgroup/cpu

sudo mount -t cgroup -o rw,nosuid,nodev,noexec,relatime,cpuacct cgroup_cpuacct /sys/fs/cgroup/cpuacct
sudo mount -t cgroup -o cpu none /sys/fs/cgroup/cpu
