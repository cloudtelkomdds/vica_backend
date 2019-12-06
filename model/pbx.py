class Pbx:
    KEY_ID_PBX = "id_pbx"
    KEY_ID_USER = "id_user"
    KEY_NAME = "pbx_name"
    KEY_LOCATION = "location"
    KEY_NUMBER_OF_EXTENSION = "number_of_extension"
    KEY_VM_NAME = "vm_name"
    KEY_VM_ADDRESS = "vm_address"
    KEY_VM_LOCAL_ADDRESS = "vm_local_address"

    def __init__(self, id_pbx, id_user, name, location, number_of_extension, vm_name, vm_address, vm_local_address):
        self.id_pbx = id_pbx
        self.id_user = id_user
        self.name = name
        self.location = location
        self.number_of_extension = number_of_extension
        self.vm_name = vm_name
        self.vm_address = vm_address
        self.vm_local_address = vm_local_address

    def get_json(self):
        return {
            self.KEY_ID_PBX: self.id_pbx,
            self.KEY_ID_USER: self.id_user,
            self.KEY_NAME: self.name,
            self.KEY_LOCATION: self.location,
            self.KEY_NUMBER_OF_EXTENSION: self.number_of_extension,
            self.KEY_VM_NAME: self.vm_name,
            self.KEY_VM_ADDRESS: self.vm_address,
            self.KEY_VM_LOCAL_ADDRESS: self.vm_local_address
        }