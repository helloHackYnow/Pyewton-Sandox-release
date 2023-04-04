import sys
import winreg as wreg


gpu_priority_keys_list = ["Software", "Microsoft", "DirectX", "UserGpuPreferences"]

def set_gpu_priority(priority:int):
    """Allows to select the gpu on which the python interpreter will execute in case of display needs.
    Only works on Windows ! (Editing the registry)

    Arguments:
        priority (int): 
            0 : GPU system default mode
            1 : GPU power saving mode
            2 : GPU high performance mode
    """
    interpreter_path = sys.executable

    new_key = wreg.HKEY_CURRENT_USER
    
    #Création du chemin de clé s'il n'exisxte pas
    for key_element in gpu_priority_keys_list:
        key = new_key
        new_key = wreg.CreateKeyEx(key, key_element, 0, wreg.KEY_CREATE_SUB_KEY)
    
    key_for_changes = wreg.OpenKey(new_key, '', 0, wreg.KEY_SET_VALUE)
    new_key.Close()
    
    #Assignation de la valeur
    wreg.SetValueEx(key_for_changes, interpreter_path, 0, wreg.REG_SZ, f"GpuPreference={priority};")
    key_for_changes.Close()
