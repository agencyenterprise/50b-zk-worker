## To execute the 50b ZK Worker on AWS:

TODO

## To execute the 50b ZK Worker on local development environment on "Mocked" mode:

### First time:

> Python version used: 3.11.8

```
python -m venv .venv
source .venv/bin/activate
cd public
pip install -r requirements.txt
```

### Execute the application:

```
cd public
./start-mocked-worker [port] [hub_url]
```

Where:  
 `port` is the port where the worker will run (Optional, default: 5000)  
 `hub_url` is the Hub URL this worker will interact (Optional, default: http://localhost:3000)

> To run multiple workers, you must run the command in different terminals using different ports:

Terminal 1: `./start-mocked-worker 5001`  
Terminal 2: `./start-mocked-worker 5002`  
Terminal 3: `./start-mocked-worker 5003`

> To run the worker using some other Hub deployment:

`./start-mocked-worker 5000 https://50b-hub.herokuapp.com`

### Check the application using these endpoints:

```
http://localhost:5000
http://localhost:5000/healthcheck
```
