# HTCondor Transfer Data

![tests](https://github.com/HTPhenotyping/htcondor_file_transfer/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/HTPhenotyping/htcondor_file_transfer/branch/master/graph/badge.svg)](https://codecov.io/gh/HTPhenotyping/htcondor_file_transfer)

This repository contains some simple files and scripts to help move and
synchronize modest amounts of data (several TBs) between two HTCondor hosts.

## Examples

```console
$ xfer.py sync pull /home/imaging_user/my_new_images /mnt/my_cold_storage --requirements='UniqueName == "TestMachine01"'`
```
