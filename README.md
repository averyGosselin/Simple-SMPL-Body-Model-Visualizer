# Body Model Visualizer

- [Body Model Visualizer](#body-model-visualizer)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Quick Demo](#quick-demo)
    - [Visualizing Your Own Data](#visualizing-your-own-data)
    - [Valid Joint Angles](#valid-joint-angles)
    - [Setting a custom Background/Environment](#setting-a-custom-backgroundenvironment)

## Introduction

This is a modified version of [body-model-visualizer](https://github.com/mkocabas/body-model-visualizer) by mkocabas, focused on adding logic to stream joint angles to visualize with the SMPL body models. 

Joint angles are expected to be streamed from a server (where joint angles are produced) with the AngleStreamingServer class in `server/`. You can then receive these angles and display them with SMPL by running the `visualizer` script in `client/`. Since the server and client can be running in completely isolated processes, we can avoid annoying dependency version collisions, which, if the project that spurred the creation of this didn't have, then I probably wouldn't have cared about, but it is cool!

## Installation

1. Clone this repository
2. In `client`:
   1. Make a venv w/ Python 3.9 (you can use something like [pyenv](https://github.com/pyenv/pyenv) to do this more cleanly)
   2. Acitvate the virtual environment
   3. Install dependencies with: ```pip install -r requirements.txt```
3. No additional setup needed for `server`, but, note it has only ever been tested with Python 3.13.
4. Download the SMPL body models in the client dir (you'll need to make an account):
   - SMPL: https://smpl.is.tue.mpg.de/ (v1.1.0)
5. Copy and rename downloaded files as necessary to `client/data/body_models`, the folder should look like:

```shell
client
└── data
   └── body_models
      ├── smpl
      │   ├── SMPL_FEMALE.pkl
      │   ├── SMPL_MALE.pkl
      │   └── SMPL_NEUTRAL.pkl
```

You should now be all set up!

## Usage

### Quick Demo

To quickly demo that the stream + visualization is working:

1. Call the `demo` method in `server/angleStreamingServer.py`
   - This will start streaming some example data
2. Run `visualizer.py` in `client` (ensuring you have activated the `client/.venv`)
   - It should connect and start collecting the stream data and displaying it

### Visualizing Your Own Data

While the demo is fun (and a great reference for how to do the steps below), it is more likely you will want to use this to visualize real data streaming from your project. In this case, you can:

1. Import the AngleStreamingServer class to your angle generating logic
2. Configure the joint keys that will be streamed, a list of available keys is included below
3. Open a streaming thread with the AngleStreamingServer's `serve_forever`
4. As joint angles are computed, send them as a dict in the format `joint_name: [X, Y, Z]` with AngleStreamingServer's `update_joint_angles`.

### Valid Joint Angles

Valid joint angles you can stream, given to the AngleStreamingServer class, include:

- {right/left}_hip
- spine1
- {right/left}_knee
- spine2
- {right/left}_ankle
- spine3
- {right/left}_foot
- neck
- {right/left}_collar
- head
- {right/left}_shoulder
- {right/left}_elbow
- {right/left}_wrist
- {right/left}_index

### Setting a custom Background/Environment

If you want to place the model in a custom environment (which is fun and cool), you can do that! To do so, you will need to add an `environment-assets` subdirectory in the `client/data` directory. There, you will need two files per environment: `{env}_ibl.ktx` and `{env}_skybox.ktx`. There are probably a lot of these available online, but you can also relatively easily make your own with:

- Some HDR imaging tool (I used the [HDReye app](https://www.hdreye.app/))
- A way to convert the exr (or hdri? idk, I got exr) file to the needed ktx files, I used [Filament](https://github.com/google/filament)
  - The command I used to convert was: ```cmgen --format=ktx --size=512 --deploy /path/to/output/dir /path/to/input.exr```, there are almost certainly other ways, but this worked for me.

By the time this is done, you should have a directory structure like:

```shell
client
└── data
    └── environment-assets
        ├── asset1_ibl.ktx
        ├── asset1_skybox.ktx
        ├── asset2_ibl.ktx
        ├── asset2_skybox.ktx
```