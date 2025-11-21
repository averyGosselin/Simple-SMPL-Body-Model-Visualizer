# Body Model Visualizer

## Introduction

This is a modified version of [body-model-visualizer](https://github.com/mkocabas/body-model-visualizer) by mkocabas, focused on adding logic to stream in joint angles to update the SMPL body model. 

Joint angles are expected to be streamed from a server (where joint angles are produced) with the AngleStreamingServer class in `server/`. The `visualizer` script in `client\` then picks these up and plots them. While a bit messy, this repo serves another project with specific dependencies that aren't compatible with open3D, so for the moment this is the easy way (I think?).

## Installation

1. Clone the repo
2. In the `client` dir:
   1. Make a venv w/ Python 3.9
   2. ```pip install -r requirements.txt```
3. No additional setup needed for `server` dir

Download the SMPL body models in the client dir (you'll need to make an account):

- SMPL: https://smpl.is.tue.mpg.de/ (v1.1.0)

Copy and rename downloaded files as necessary into `client/data/body_models` in this repo, the folder should look like:

```shell
client
└── data
    └── body_models
        ├── smpl
        │   ├── SMPL_FEMALE.pkl
        │   ├── SMPL_MALE.pkl
        │   └── SMPL_NEUTRAL.pkl
```

To demo things working, you can: 

1. Call the `demo` method in `server/angleStreamingServer.py`
   1. This will start streaming random data to the configured port
2. Run `visualizer.py` in `client`
   1. It should connect and start collecting the stream data, moving the left arm

Ideally, you will be able to just import the AngleStreamingServer class to where angles are being produced and stream them from there. Then when you want to visualize you just have to run `visualizer.py`.