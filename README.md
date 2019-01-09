# Manim on Mac OS

Manim is an animation engine for explanatory math videos. It's used to create precise animations programmatically.

## Installation

1. Install Python3.7

   - <https://www.python.org/downloads/release/python-371/>

     Or you can install with brew

     `brew install python3`

2. Install latex 

   - https://miktex.org/download>

3. Install cairo ffmpeg pgk-config and sox with brew

   ```shell
   brew install cairo
   brew install pkg-config
   brew install ffmpeg
   brew install sox
   ```

4. Clone the Manim

1. ```shell
   git clone https://github.com/3b1b/manim.git
   cd manim
   pip3 install -r requirements.txt  //You may be failed on Mac with pip, but pip3 is OK.
   ```

## Using virtualenv

1. Install with pip

​       `pip3 install virtualenv`

2. Creat a env and get into env

   `virtualenv venv`

   `source venv/bin/activate`

   - You may meet error here. To solve it you can follow next

      `source ~/venv/bin/activate`

   - You can get out of the env with

     `deactivate`

##Do a little modify

Find `constant.py` in your `manim` and get to line 23 ,find that says "Dropbox(3Blue1Brown)/3Blue1Brown Team Folder". We need to change this line to match the output folder you just created. In my case, I replaced that line with `manim/media`. You should replace it with whatever your file path is (keeping in mind that “~” in the line above is a short for the file path to your home directory).

```python
else:
    MEDIA_DIR = os.path.join(
        os.path.expanduser('~'),
        "manim.media"
    )
```



## Test

Remember to start in the venv and in the path `manim`

   `python3 extract_scene.py example_scenes.py SquareToCircle -p`

   `python3 extract_scene.py example_scenes.py UdatersExample -p`

Now, you can find the vedio created in `manim/media` 

You are succeed if there is no error.

<!--第一次英文写markdown，以后还是写中文吧-->

