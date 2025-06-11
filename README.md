# Bioluminescent Organoid Segmentation & Tracking (BIOST)

A Python toolkit and standalone app for analyzing bioluminescent organoid data.
BIOST combines a cellpose pretrained algorithm fine tuned with bioluminescent organoid data with a tracking tool to monitor the size and the bioluminescence of the organoids.

## Features

- Segmentation using Cellpose
- Tracking
- GUI

## Installation

If you use the standalone, please proceed this way to download it:
- Install git on your computer: https://git-scm.com/downloads
- In the windows powershell type the following commands:
```powershell
cd your/path/to/save/BIOST
git lfs install
git clone https://github.com/NeriJeremy/BioluminescentOrganoidSegmentationTracking-BIOST-.git
git lfs pull
```
## Citations

If you use this code, please also cite the following tools:

- **Cellpose**:
  > Stringer, C., Wang, T., Michaelos, M. & Pachitariu, M.  
  > Cellpose: a generalist algorithm for cellular segmentation.  
  > Nature Methods 18, 100–106 (2021).  
  > [https://doi.org/10.1038/s41592-020-01018-x](https://doi.org/10.1038/s41592-020-01018-x)

- **Trackpy**:
  > Allan, D.B., Caswell, T.A., Keim, N.C. et al.  
  > Trackpy: Trackpy v0.4.2 (2019).  
  > [https://doi.org/10.5281/zenodo.3492186](https://doi.org/10.5281/zenodo.3492186)