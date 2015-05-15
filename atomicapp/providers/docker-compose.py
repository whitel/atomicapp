from atomicapp.plugin import Provider

from collections import OrderedDict
import os, anymarkup, subprocess

import logging
import shutil
#from constants import APP_ENT_PATH, ANSWERS_FILE, MAIN_FILE, DEFAULT_PROVIDER


logger = logging.getLogger(__name__)

class DockerComposeProvider(Provider):
    key = "docker-compose"
    dc = "docker-compose"

    def init(self):
        cmd_check = ["docker", "version"]
        docker_version = subprocess.check_output(cmd_check).split("\n")

        client = ""
        server = ""
        for line in docker_version:
            if line.startswith("Client API version"):
                client = line.split(":")[1]
            if line.startswith("Server API version"):
                server = line.split(":")[1]

        if client > server:
            raise Exception("Docker version in app image (%s) is higher than the one on host (%s). Please update your host." % (client, server))

        if not self.dryrun and self.container:
            self.dc = "/host/usr/bin/docker-compose"

    def _callDockerCompose(self):
        #unfortunately, docker-compose does not take a filename as a param
        cmd = [self.dc, "up", "-d"]
        logger.info("Calling: %s" % " ".join(cmd))

        if not self.dryrun:
            subprocess.check_call(cmd) == 0

    def deploy(self):
        for artifact in self.artifacts:
            artifact_path = os.path.join(self.path, artifact)
            target_docker_compose_yml = os.path.join("./", os.path.split(artifact)[1])
            logger.debug("artifact_path: %s; artifact: %s; target_docker_compose_yml: %s" % (artifact_path, artifact, target_docker_compose_yml))
            logger.info("Writing populated yml file to %s" % target_docker_compose_yml)
            try:
                os.remove(target_docker_compose_yml) 
            except:
                pass #ignore exceptions

            shutil.copyfile(artifact_path, target_docker_compose_yml)
            logger.info("RUN label is currently ignored")

            self._callDockerCompose()
