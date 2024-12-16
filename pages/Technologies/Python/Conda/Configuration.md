* `conda create -n myenv` => DO NOT USE
	=> this will create a conda environment in .conda/envs. Probably not what you want.

* `conda create -p [PATH]`
	=> This creates a conda environment in the path specified. This is the preferred option, because you would use the project-directory for the PATH.
* `conda create --name py38_env -c https://repo.anaconda.com/pkgs/snowflake python=3. numpy pandas`	=> create env with specified python version
* `conda config --set env_prompt '({name})' `
	=> To avoid long path names as command prompt
* `conda activate . `
* => Activate the conda environment. Execute this command from within the conda environment directory
* `conda install altair -p . `
	=> The dot at the end means the current path
* `conda remove -n ENV_NAME --all` => remove conda environment


