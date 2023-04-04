import py_compile
import json


str_to_add = "from Body import Body\nfrom decimal import Decimal\n\ndef computeNorme(a:Body, b:Body):\n  return "

def generate_code(json_path):
    with open(json_path) as file:
        compute_rules = json.load(file)
        file.close()
    
    for rule in compute_rules:
        script_name = rule["name"].replace(" ", "_")+".py"
        script_path = f"computation_rules/{script_name}"
        str_script = str_to_add + rule["norme_formula"]
        
        try:
            with open(script_path, "x") as script:
                script.write(str_script)
                script.close()
        except:
            with open(script_path, "w") as script:
                script.write(str_script)
                script.close()
        try:
            py_compile.compile(script_path)
        except:
            print(f"Error trying to compile the compute script {rule['name']}")
