# minesweeper-ai
Implementation of the classic minesweeper game, with an AI agent

#### To run in WSL2 on Win10:
In Windows10 launch Xlaunch, making sure to select `Disable Access Control`. This starts the Xming X server, to use as a GUI output device. Available from [Sourceforge](https://sourceforge.net/projects/xming/).

You might also need to set the `DISPLAY` variable in WSL2:
  `export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0`

In runner.py, it might be necessary to add the following line to suppress audio errors:
  `os.environ["SDL_AUDIODRIVER"]="dsp"`

Then launch: `python runner.py`
