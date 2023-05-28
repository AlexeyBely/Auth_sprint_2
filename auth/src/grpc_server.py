import grpc
import uuid
import logging
from concurrent import futures

from grpc_control import roles_control_pb2_grpc
from grpc_control.roles_control_server import RolesControl
from settings import api_settings as _as


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    roles_control_pb2_grpc.add_RolesControlServicer_to_server(
        RolesControl(), server)
    server.add_insecure_port(f'[::]:{_as.grpc_port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()