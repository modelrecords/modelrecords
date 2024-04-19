# Planecards
The wonderful world of plane cards.

## Technical documentation
1) [Techincal Design Document](https://docs.google.com/document/d/18ebXWaUiy-wSAZHtXMSESnIHMjJoV-GeW0W9i-uhlDo/edit#heading=h.n2dkl2j6xzna)


## Dev startup
It's time to setup your environment!
1. Install `brew install --cask anaconda`
2. Activate the conda environment via `conda activate planecards`
3. Update your dependencies! `conda env update --file environment.yml`
4. You might have to reactivate the conda environment via `conda activate planecards`

## Playing with jupyter notebooks
If you are enthused about using the `.ipynb` files you can set the environment to `planecards` and you should be off to the races!

## PDF Rendering
If you want to render PDFs, and let's be honest who doesn't, you must do the following:
1. Install MacTex `brew install --cask mactex`
2. If you have to interrupt the build or it crashes, you'll have to rerun the following in order to build again:
    1. `conda env update --file environment.yml`
    2. `conda activate planecards`

## Website Rendering
The code for the website lives in `planecards/web` and uses Pelican + Tailwindcss

### Running locally
1. Run the steps under Dev startup
2. Navigate into `planecards/web/example.com`
3. Run `invoke livereload` in one terminal
4. Run `tailwindcss -i input.css -o themes/planecards/static/css/main.css --watch` in another terminal

#### Editing
1. The project uses [tailwindcss](https://tailwindcss.com/docs/installation)
2. Editing of template html is done in `themes/planecards/templates`
3. Editing of page html is done in `themes/planecards/content/pages`

### Running in production
...
