import googleapiclient.discovery
import os
import requests
import threading
import time
from instance import Instance
from Database import Database

class VmManager:
    DEFAULT_CONFIG = {
        "machineType": "https://www.googleapis.com/compute/v1/projects/handy-digit-259807/zones/asia-southeast1-b/machineTypes/custom-1-1024",
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": "https://www.googleapis.com/compute/v1/projects/handy-digit-259807/global/images/asterisk-server"
                }
            }
        ],
        "networkInterfaces": [
            {
                "network": "https://www.googleapis.com/compute/v1/projects/handy-digit-259807/global/networks/default",
                "accessConfigs": [
                    {
                        "type": "ONE_TO_ONE_NAT",
                        "name": "External NAT"
                    }
                ]
            }
        ]
    }
    DEFAULT_PROJECT = "handy-digit-259807"
    DEFAULT_ZONE = "asia-southeast1-b"

    DEFAULT_SIP_GENERAL_CONFIG = \
        "[general]\n" + \
        "externip={0}\n" + \
        "localnet={1}/255.255.255.255\n" + \
        "\n"

    DEFAULT_SIP_EXTENSIONS_CONFIG = \
        "[{0}]\n" + \
        "type=friend\n" + \
        "host=dynamic\n" + \
        "username={1}\n" + \
        "secret={2}\n" + \
        "canreinvite=no\n" + \
        "nat=yes\n" + \
        "context=phones\n" + \
        "dtmfmode=rfc2833\n" + \
        "allow=all\n" + \
        "\n"

    DEFAULT_EXTENSIONS_GENERAL_CONFIG = \
        "[general]\n" + \
        "static=yes\n" + \
        "writeprotect=no\n" + \
        "\n" + \
        "[phones]\n"

    DEFAULT_EXTENSIONS_EXTENSIONS_CONFIG = \
        "exten => {0},1,Dial(SIP/{1})\n"

    DEFAULT_HEADER = {
        "Authorization": "Bearer MyNG8CZkYP3zDD6j3H891P4JHhcsnQRu4XwUE1ix"
    }

    DEFAULT_WAITING_TIME_IN_SECONDS = 3

    DEFAULT_EXTENSIONS = [
        {
            "username": "99999",
            "secret": "99999"
        },
        {
            "username": "88888",
            "secret": "88888"
        }
    ]

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account_vica.json"
        self.compute = googleapiclient.discovery.build("compute", "v1")

    def run(self, name):
        try:
            VmManager.DEFAULT_CONFIG["name"] = name
            self.compute.instances().insert(project=VmManager.DEFAULT_PROJECT,
                                            zone=VmManager.DEFAULT_ZONE,
                                            body=VmManager.DEFAULT_CONFIG).execute()
            threading.Thread(target=self.prepare_instance, args=(name,)).start()
        except Exception as e:
            raise e

    def get_instances(self):
        result = self.compute.instances().list(project=VmManager.DEFAULT_PROJECT,
                                               zone=VmManager.DEFAULT_ZONE).execute()
        instances = []
        for item in result["items"]:
            print(item)
            try:
                instance = Instance(
                    name=item["name"],
                    external_address=item["networkInterfaces"][0]["accessConfigs"][0]["natIP"],
                    local_address=item["networkInterfaces"][0]["networkIP"]
                )
                instances.append(instance)
            except Exception as e:
                pass
        return instances

    def prepare_instance(self, name):
        print("Preparing instance " + name)
        preparation_success = 0
        selected_instance = None
        while not preparation_success:
            time.sleep(VmManager.DEFAULT_WAITING_TIME_IN_SECONDS)
            print("Trying to get instance " + name)
            instances = self.get_instances()
            for instance in instances:
                if instance.name == name:
                    try:
                        self.update_sip_config(external_address=instance.external_address,
                                               local_address=instance.local_address,
                                               extensions=self.DEFAULT_EXTENSIONS)
                        self.update_extensions_config(external_address=instance.external_address,
                                                      extensions=self.DEFAULT_EXTENSIONS)
                        preparation_success = 1
                        selected_instance = instance
                    except Exception as e:
                        pass
        query = "UPDATE tb_pbx SET vm_address = %s, vm_local_address = %s WHERE vm_name = %s"
        param = [selected_instance.external_address, selected_instance.local_address, selected_instance.name]
        _ = Database.execute(operation=Database.WRITE, query=query, param=param)
        print("Finish preparing instance " + name)

    @staticmethod
    def generate_sip_config(external_address, local_address, extensions):
        sip_config = VmManager.DEFAULT_SIP_GENERAL_CONFIG.format(external_address, local_address)
        for extension in extensions:
            sip_extensions_config = VmManager.DEFAULT_SIP_EXTENSIONS_CONFIG.format(extension["username"],
                                                                                   extension["username"],
                                                                                   extension["secret"])
            sip_config = sip_config + sip_extensions_config
        return sip_config

    @staticmethod
    def update_sip_config(external_address, local_address, extensions):
        sip_config = VmManager.generate_sip_config(external_address=external_address,
                                              local_address=local_address,
                                              extensions=extensions)
        url = "http://{0}:5000/write_sip".format(external_address)
        requests.post(url=url,
                      data={
                          "config_string": sip_config
                      },
                      headers=VmManager.DEFAULT_HEADER)

    @staticmethod
    def generate_extensions_config(extensions):
        extensions_config = VmManager.DEFAULT_EXTENSIONS_GENERAL_CONFIG
        for extension in extensions:
            extensions_extensions_config = VmManager.DEFAULT_EXTENSIONS_EXTENSIONS_CONFIG.format(
                extension["username"], extension["username"])
            extensions_config = extensions_config + extensions_extensions_config
        return extensions_config

    @staticmethod
    def update_extensions_config(external_address, extensions):
        extensions_config = VmManager.generate_extensions_config(extensions=extensions)
        url = "http://{0}:5000/write_extensions".format(external_address)
        requests.post(url=url,
                      data={
                          "config_string": extensions_config
                      },
                      headers=VmManager.DEFAULT_HEADER)

    def remove(self, name):
        result = self.compute.instances().delete(project=VmManager.DEFAULT_PROJECT,
                                        zone=VmManager.DEFAULT_ZONE,
                                        instance=name).execute()

    def get_valid_name(self, id_user, name):
        name = name.lower().replace(" ", "-") + "-" + str(id_user)
        return name

    def get_vm_address(self, name):
        instances = self.get_instances()
        for instance in instances:
            if instance.name == name:
                return instance.external_address

if __name__ == "__main__":
    v = VmManager()
    instances = v.get_instances()
    for instance in instances:
        print(instance)