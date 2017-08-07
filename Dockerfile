# Use Ubuntu 14.04 LTS
FROM ubuntu:trusty-20170119

# Install FSL 5.0.9
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL http://neuro.debian.net/lists/trusty.us-ca.full >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 0xA5D32F012649A5A9 && \
    apt-get update && \
    apt-get install -y fsl-core=5.0.9-4~nd14.04+1 && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure environment
ENV FSLDIR=/usr/share/fsl/5.0
ENV FSL_DIR="${FSLDIR}"
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=/usr/lib/fsl/5.0:$PATH
ENV FSLMULTIFILEQUIT=TRUE
ENV POSSUMDIR=/usr/share/fsl/5.0
ENV LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLWISH=/usr/bin/wish
ENV FSLOUTPUTTYPE=NIFTI_GZ
#RUN echo "cHJpbnRmICJrcnp5c3p0b2YuZ29yZ29sZXdza2lAZ21haWwuY29tXG41MTcyXG4gKkN2dW12RVYzelRmZ1xuRlM1Si8yYzFhZ2c0RVxuIiA+IC9vcHQvZnJlZXN1cmZlci9saWNlbnNlLnR4dAo=" | base64 -d | sh

RUN apt-get update && apt-get install -y --no-install-recommends python-pip python-six python-nibabel python-setuptools python-pandas && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN pip install pybids==0.0.1
ENV PYTHONPATH=""

# Install git
RUN apt-get -y update && \
    apt-get -y install git-all

# Install MCR 2012a v717
RUN apt-get install unzip
RUN mkdir /MCR_2014a && cd $_ && \
    wget https://www.mathworks.com/supportfiles/downloads/R2014a/deployment_files/R2014a/installers/glnxa64/MCR_R2014a_glnxa64_installer.zip -O MCR_R2014a_glnxa64_installer.zip && \
    unzip MCR_R2014a_glnxa64_installer.zip && ./install -mode silent -agreeToLicense yes -destinationFolder /opt -outputFile /matlab_installer.log

# Install R
RUN sh -c 'echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list' && \
    gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9 && \
    gpg -a --export E084DAB9 | sudo apt-key add - && \
    apt-get update && \
    apt-get -y install r-base

# Get ICA FIX
RUN cd / && wget http://users.bmap.ucla.edu/~yeunkim/ftp/fix1.065.dhcp8.tar.gz -O fix.tar.gz && \
    tar xvfz fix.tar.gz
RUN mv /fix1.065 /fix1.06a

#COPY /opt/HCP-Pipelines/ICAFIX/hcp_fix.for_fix1.06a /fix1.06a

RUN cd / && mkdir /rpackages
COPY rpackages.sh /rpackages/rpackages.sh
RUN chmod +x /rpackages/rpackages.sh
COPY rpackages.txt /rpackages/rpackages.txt
RUN cd /rpackages && bash rpackages.sh

#install connectome workbench
RUN apt-get update && apt-get -y install connectome-workbench=1.2.3-1~nd14.04+1
ENV CARET7DIR=/usr/bin

#COPY hcpbin /hcpbin
COPY run.py /run.py
RUN chmod +x run.py
#RUN chmod +x /hcpbin/wrapper.py
#COPY fsf_templates /fsf_templates
#RUN chmod +x /fsf_templates/scripts/generate_level1_fsf.sh

#COPY version /version

#ENTRYPOINT ["/hcpbin/wrapper.py"]
ENTRYPOINT ["/run.py"]
