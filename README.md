# Asyncy git server

Deploy your application via

```sh
git push asyncy master
```

This project is a very simple http server that accepts `git push` events.
It will accept the contents, checkout the branch and run Asyncy release story.

## Development

#### Setup

```shell
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Run

```shell
source venv/bin/activate
python -m app.main --logging=debug --debug=true --port=8888 --engine=localhost:8889
```

Assuming the Asyncy Engine is not running so let's create a fake server.
```shell
source venv/bin/activate
python -m tests.FakeServer --logging=debug --debug=true --port=8889
```

#### Push

```shell
git remote add asyncy http://localhost:8888
git push asyncy master
```

✨ 🍰 ✨
