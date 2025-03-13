import subprocess


def run(oas_file:str, domain_file:str):
    res = subprocess.run([
            "datamodel-codegen",
            "--use-field-description",
            "--use-schema-description",
            "--use-operation-id-as-name",
            "--reuse-model",
            "--input", oas_file,
            "--output", domain_file
        ], 
        # cwd=self.cwd,
        capture_output=True, 
        text=True
    )
    if res.returncode != 0:
        raise Exception(res.stderr)