import json
import os

import dotenv

from policy_adherence.llm.litellm_model import LitellmModel

dotenv.load_dotenv()
model = "gpt-4o-2024-08-06"
aw = LitellmModel(model)
input_file = "/Users/naamazwerdling/Documents/OASB/policy_validation/orca/init.json"
output_dir = "/Users/naamazwerdling/Documents/OASB/policy_validation/orca/"
prompt = "Please create a detailed open api spec in json format for the following function using the data below. Make sure to use operationId and the path name set is as the function name. Make sure not to use references but all information should be under the relevant place."
with open(input_file, 'r') as file:
    data = json.load(file)
for domain,actions in data.items():
	print(domain)
	oas = {
  "openapi": "3.0.3",
  "info": {
    "title": domain,
    "description": "An API for "+domain,
    "version": "1.0.0"
  },
  "paths": {}
	}
	dir = os.path.join(output_dir,domain)
	if not os.path.isdir(dir):
		os.makedirs(dir)
	if not os.path.isdir(os.path.join(dir,"actions")):
		os.makedirs(os.path.join(dir,"actions"))
	for a in actions:
		aname = a["name"]
		print(aname)
		resp = aw.chat_json([{"role": "system", "content": prompt},{"role": "user", "content": "function: "+aname+"\ndata: "+json.dumps(a)}])
		with open(os.path.join(output_dir, domain,"actions", aname+".json"), "w") as outfile:
			json.dump(resp, outfile, indent=4)
		path = resp['paths']["/"+aname]
		oas["paths"]["/"+aname]=resp['paths']["/"+aname]
		
	with open(os.path.join(output_dir,domain,"oas.json"), "w") as outfile:
		json.dump(oas, outfile, indent=4)