cd docker-pyngsi/
docker build -t pyngsi-notebook .

#git clone https://github.com/jupyter/docker-stacks.git
#cd docker-stacks/
#cd base-notebook/
#docker build -t base-notebook --build-arg PYTHON_VERSION=3.8 .
#docker build -t minimal-notebook --build-arg BASE_CONTAINER=base-notebook .

#python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
#pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyngsi

python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
pip install pypi

docker run --name pyngsi-notebook -d -p 8888:8888 -v "$PWD"/notebook:/home/jovyan/work pyngsi-notebook:latest
docker exec -it pyngsi-notebook jupyter notebook list