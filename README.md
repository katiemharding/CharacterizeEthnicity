# CharacterizeEthnicity

## Characterization of deletions and duplications

### Objective

Write code to characterize the deletion and duplication frequencies and breakpoint positions on a per-ethnicity basis.

### Analysis Overview

Each sample will have a slightly different copy number at each probe location. This means that we can use the non_CNSL probes to standardize the counts. The non_CNSL probes should have 2 copies. Any CNSL probe with less than half the counts of the non_CNSL probes represents a deletion. Any CNSL probe with more than 1.5 times the counts represents a duplication. A duplication or deletion is 4 probes that all show increased or decreased copies.

### Steps

1) Data Import

2) Non CNSL Probe Variability: Characterize the non_CNSL probes by finding the mean value for the sample

3) Label poor performing probes: For each sample divide the mean non_CNSL probe value by the individual probes counts Find probematic probes by examining the variability of those counts

4) Lable Breakpoints: Count continuious probes with deletions/duplications to find breakpoints

5) Output: the breakpoint positions, and the number of probes in that breakpoint
