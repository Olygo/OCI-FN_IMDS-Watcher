# OCI-FN_IMDS-Watcher

The instance metadata service is available in two versions, version 1 and version 2. 

IMDSv2 offers increased security compared to v1. We **strongly** recommend you disable IMDSv1 and allow requests only to IMDSv2

While launching compute instances with default options, both IMDSv1 and IMDSv2 are enabled.

This OCI Function automatically updates [Instance metadata service to v2](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/gettingmetadata.htm#upgrading-v2) after compute instance launch.

## How-to 

Read the step by step guide to quickly set up your environment and deploy your function to OCI:
[OCI_Function_QuickStart.pdf](./OCI_Function_QuickStart.pdf)

## Function files

- func.py
- func.yaml
- requirements.txt

These three files must be located in the function folder.

## Questions ?
**_olygo.git@gmail.com_**


## Disclaimer
**Please test properly on test resources, before using it on production resources to prevent unwanted outages or unwanted bills.**
