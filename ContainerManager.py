import docker

class ContainerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.image = "flaviostutz/freepbx"

        #TODO: For now, make it static. Find way to obtain it from NIC
        self.host_address = "3.217.77.161"
        self.container_address = "127.0.0.1"

    def run(self, name, host_port):
        self.client.containers.run(image=self.image,
                                   detach=True,
                                   name=name,
                                   ports={"80/tcp": host_port})

    def remove(self, name):
        self.client.containers.get(name).remove(force=True)

    def list(self):
        print(self.client.containers.list())

    def get_port(self, used_ports):
        if len(used_ports) == 0:
            return 30001
        for port in range(30002, 40001):
            if port not in used_ports[0]:
                return port

    def get_valid_name(self, id_user, name):
        name = str(id_user) + "_" + name.lower().replace(" ", "_")
        return name

    def get_host_address(self):
        return self.host_address

    def get_container_address(self):
        return self.container_address
