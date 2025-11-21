# Body Model Visualizer

## Introduction

This is a modified version of [body-model-visualizer](https://github.com/mkocabas/body-model-visualizer) by mkocabas, focused on adding logic to stream in joint angles to update the SMPL body model.

## Installation

1. Clone the repo
2. Make a venv w/ Python 3.9 (I used 3.8.10 and it worked too)
3. Install the requirements:

```shell
pip install -r requirements.txt
```

Download the SMPL body models (you'll need to make an account):

- SMPL: https://smpl.is.tue.mpg.de/ (v1.1.0)

Copy and rename downloaded files as necessary into `data/body_models` in this repo, the folder should look like:

```shell
data
└── body_models
    ├── smpl
    │   ├── SMPL_FEMALE.pkl
    │   ├── SMPL_MALE.pkl
    │   └── SMPL_NEUTRAL.pkl
```

Right now there's a mini demo script in `visualizer.py`, you can run this with:

```shell
python visualizer.py
```

This should step through rotations of the shoulder and elbow joints. viz.update_body_pose can be used to update shoulder and elbow angles given in XYZ format. To add more joints we can add them to the SMPLStreamingVisualizer and extend the update_body_pose method, but hopefully shouldn't be too difficult.
