# Quickstart for parareq

This will contain the tutorial for getting start with parareq but it's WIP rn though. Refer to the README for basic information getting started. 


## OpenAI Usage

We default to using openai, you need to setup your API key

### Setup API Key

You have three options to set up your environment variable for the OpenAI API key:

- One option is to export the environment variable every time you open the terminal. You can add the export command to your .bashrc file to avoid this.
    - `export OPENAI_API_KEY=[add your api key here]`
- Another option is to 
    1. create a copy of the `.env.template` file and name it `.env`. 
    2. Then, you can add your OpenAI API key in the `.env` file.
- finally, you can provide as a cli argument e.g. `parareq --api_key "XYZABCEFG"`

### Run OpenAI calls

Having set your API key in an accessible place, now just run:
```
parareq     \ 
         --requests_filepath examples/input/salt_survey_example.jsonl \
         --save_filepath output/response_salt_survey_example.jsonl \
         --request_url https://api.openai.com/v1/chat/completions
```



## HuggingFace usage
You need to set the enviromental variable 
To use huggingface is then just do: 

``` bash
parareq  --requests_filepath examples/input/huggingface_example.jsonl \
         --save_filepath examples/data/huggingface_example_response.jsonl \
         --which_api huggingface \
         --request_url https://api-inference.huggingface.co/models/bert-base-uncased
```



## API usage 

This not particularly stable tbh, but you can get start as follow below:
``` python
from parareq import APIRequestProcessor
processor = APIRequestProcessor(api_key="xyz")
processor.run("request.cfg")
```

