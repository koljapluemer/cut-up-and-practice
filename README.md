# Cut Up and Practice

> These feats are routine at Meadowmount, in part because the teachers take the idea of chunking to its extreme. Students scissor each measure of their sheet music into horizontal strips, which are stuffed into envelopes and pulled out in random order. They go on to break those strips into smaller fragments by altering rhythms.

— [The Talent Code](https://www.goodreads.com/book/show/5771014-the-talent-code)

![Screenshot of Cut Up And Practice](/doc/img/project.png)

This project allows you to practice music by "cutting up" a piece of music into snippets and practicing them, one after the other. It follows the principles of *Deliberate Practice*, *Chunking*, and *Spaced Repetition*.

*Cut Up and Practice* is in an early stage of development. You can run it and use it to practice almost any instrument, but expect rough edges and missing features.

## How It Works

1. Find a piece of music that you want to practice (e.g. sheet music)
2. "Cut it" into small pieces using a screenshot tool of your choice
3. Put all screenshots into a folder
4. Start *Cut Up and Practice*, load up the folder and auto-generate "snippets"
5. Practice!

*Also see demo video below:*

![Cut Up and Practice Demo Use Case](doc/img/demo_video.mp4)

## Contributing & Running Locally

*Release files that allow you to run this app with one click are WIP. For now, it has to be installed manually.*

1. clone this repository to your local machine
2. make sure Python is installed
3. create and activate a `virtualenv`
4. get dependencies, e.g. with `pip install -r requirements.txt`
5. run `python src/app.py`


*I am happy about any contribution, issue of feedback :)*

### Building

1. Run `pyinstaller src/app.py --hidden-import=PIL._tkinter_finder --hidden-import=pony.orm.dbproviders --hidden-import=pony.orm.dbproviders.sqlite`

## Credit

- executable app made with [pyinstaller](https://github.com/pyinstaller/pyinstaller/tree/5d7a0449ecea400eccbbb30d5fcef27d72f8f75d)
- using [ebisu](https://github.com/fasiha/ebisu) for exercise selection
- other stack:
	- `tkk`
	- `Pony ORM`

