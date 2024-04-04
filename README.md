## To execute the 50b ZK Worker on AWS:

TODO

## To execute the 50b ZK Worker on local development environment using "Mocked" mode:

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
./start-mocked-worker.sh [port] [hub_url] [worker_wallet]
```

Where:  
`port` is the port where the worker will run (Optional, default: 5000)  
`hub_url` is the Hub URL this worker will interact (Optional, default: http://localhost:3000)  
`worker_wallet` is the Worker wallet addres that will receive payments (Optional, default: 0x80963163d664fD34fc2e15104904CBba213377b3)

To run multiple workers, you must run the command in different terminals using different ports:  
Terminal 1: `./start-mocked-worker.sh 5001`  
Terminal 2: `./start-mocked-worker.sh 5002`  
Terminal 3: `./start-mocked-worker.sh 5003`

To run the worker using some other Hub deployment and wallet:  
`./start-mocked-worker.sh 5000 https://50b-hub.herokuapp.com 0xB05Cb6716938dc10a48AF2dC73822f3F3FF5b422`

> You can change the environment variables in `start-mocked-worker.sh` script

### Check the application using these endpoints:

```
http://localhost:5000
http://localhost:5000/healthcheck
```
