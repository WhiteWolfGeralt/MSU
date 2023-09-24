set -o xtrace

setup_root() {
    apt-get install -qq -y \
        python3-pip \
        python3-tk

    pip3 install -qq \
        pytest \
        scikit-image \
        h5py \
        catboost \
        hyperopt \
        ipywidgets \
        keras \
        lightgbm \
        matplotlib \
        numpy \
        pandas \
        plotly \
        scipy \
        seaborn \
        scikit-learn \
        torch \
        torchvision \
        tqdm \
        umap-learn \
        xgboost \
        pep8
}

setup_checker() {
    python3 -c 'import matplotlib.pyplot'
}

"$@"