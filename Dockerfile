FROM nvidia/cuda:9.0-cudnn7-devel

# Install system dependencies
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  	build-essential \
  	curl \
  && apt-get clean

# Install python miniconda3 + requirements
ENV MINICONDA_HOME="/opt/miniconda"
ENV PATH="${MINICONDA_HOME}/bin:${PATH}"
RUN curl -o Miniconda3-latest-Linux-x86_64.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  && chmod +x Miniconda3-latest-Linux-x86_64.sh \
  && ./Miniconda3-latest-Linux-x86_64.sh -b -p "${MINICONDA_HOME}" \
  && rm Miniconda3-latest-Linux-x86_64.sh
WORKDIR /root
COPY pip.txt pip.txt
COPY conda.txt conda.txt
COPY conda-gpu.txt conda-gpu.txt
COPY Makefile Makefile
RUN make python-deps GPU=1
RUN conda clean -y -i -l -p -t

# Create project folder
RUN mkdir neurowriter
WORKDIR /neurowriter

# Define locale
ENV LANG C.UTF-8  
ENV LC_ALL C.UTF-8

# Launche Jupyter notebook with appropriate options
CMD jupyter notebook --allow-root --no-browser --ip='*'

