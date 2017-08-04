#!/bin/bash

# pull r package tar balls
wget https://cran.r-project.org/src/contrib/mvtnorm_1.0-6.tar.gz
wget https://cran.r-project.org/src/contrib/modeltools_0.2-21.tar.gz
wget https://cran.r-project.org/src/contrib/strucchange_1.5-1.tar.gz
wget https://cran.r-project.org/src/contrib/TH.data_1.0-8.tar.gz
wget https://cran.r-project.org/src/contrib/multcomp_1.4-6.tar.gz
wget https://cran.r-project.org/src/contrib/coin_1.2-1.tar.gz
wget https://cran.r-project.org/src/contrib/lattice_0.20-35.tar.gz
wget https://cran.r-project.org/src/contrib/zoo_1.8-0.tar.gz
wget https://cran.r-project.org/src/contrib/sandwich_2.4-0.tar.gz
wget https://cran.r-project.org/src/contrib/Archive/party/party_1.0-25.tar.gz

wget https://cran.r-project.org/src/contrib/e1071_1.6-8.tar.gz
wget https://cran.r-project.org/src/contrib/kernlab_0.9-25.tar.gz
wget https://cran.r-project.org/src/contrib/class_7.3-14.tar.gz

wget https://cran.r-project.org/src/contrib/gplots_3.0.1.tar.gz
wget https://cran.r-project.org/src/contrib/bitops_1.0-6.tar.gz
wget https://cran.r-project.org/src/contrib/gtools_3.5.0.tar.gz
wget https://cran.r-project.org/src/contrib/gdata_2.18.0.tar.gz
wget https://cran.r-project.org/src/contrib/caTools_1.17.1.tar.gz
wget https://rocr.bioinf.mpi-sb.mpg.de/ROCR_1.0-5.tar.gz

wget https://cran.r-project.org/src/contrib/randomForest_4.6-12.tar.gz
wget https://cran.r-project.org/src/contrib/MASS_7.3-47.tar.gz


R CMD INSTALL kernlab_0.9-25.tar.gz
R CMD INSTALL `cat rpackages.txt`
