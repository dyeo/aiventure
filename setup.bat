@echo off
rem Update core python dependencies
python -m pip install --upgrade pip wheel setuptools virtualenv
rem Create virtual environment for project
python -m virtualenv __env__
rem Activate the virtual environment and install dependencies in it
call __env__/Scripts/activate.bat
python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.* kivy_deps.glew==0.1.* --no-cache-dir
python -m pip install kivy_deps.gstreamer==0.1.* --no-cache-dir
python -m pip install kivy==1.11.1 --no-cache-dir
python -m pip install torch===1.5.0 torchvision===0.6.0 -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install transformers
python -m pip install func_timeout
