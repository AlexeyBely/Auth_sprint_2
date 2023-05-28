import grpc
import uuid
import logging
from concurrent import futures

from grpc_control import roles_control_pb2_grpc
from grpc_control import roles_control_pb2
from database.db_models import User, UserRole
from database.db_psql import session_psql
from settings import api_settings as _as
from storage_token import get_storage_tokens


class RolesControl(roles_control_pb2_grpc.RolesControlServicer):

    def __init__(self):
        self.user_m = User
        self.role_m = UserRole
        self.session = session_psql
        self.storage = get_storage_tokens()

    def GetUserInfo(self, request, context):
        with self.session() as db:
            user = self._get_item_by_id(db, self.user_m, request.id)
            return roles_control_pb2.UserInfo(email=user.email)
    
    def CreateRole(self, request, context):
        with self.session() as db:
            role = self.role_m(name=request.name)
            db.add(role)
            db.commit()
            return roles_control_pb2.Uuid(id=str(role.id))
    
    def UpdateRole(self, request, context):
        with self.session() as db:
            role = self._get_item_by_id(db, self.role_m, request.role_id)
            if role is None:
                return roles_control_pb2.OperationResult(successful=False)    
            role.name = request.name
            db.add(role)
            db.commit()
            return roles_control_pb2.OperationResult(successful=True)

    def ProvideRoleUser(self, request, context):
        with self.session() as db:
            user = self._get_item_by_id(db, self.user_m, request.user_id)
            if user is None:
                return roles_control_pb2.OperationResult(successful=False) 
            role = self._get_item_by_id(db, self.role_m, request.role_id)
            if role is None:
                return roles_control_pb2.OperationResult(successful=False)
            user.roles.append(role)
            db.add(user)
            db.commit()
            self.storage.set_token_to_compromised(request.jti_to_compromised)
            return roles_control_pb2.OperationResult(successful=True)

    def RevokeRoleUser(self, request, context):
        with self.session() as db:
            user = self._get_item_by_id(db, self.user_m, request.user_id)
            if user is None:
                return roles_control_pb2.OperationResult(successful=False) 
            role = self._get_item_by_id(db, self.role_m, request.role_id)
            if role is None:
                return roles_control_pb2.OperationResult(successful=False)
            user.roles.remove(role)
            db.commit()
            self.storage.set_token_to_compromised(request.jti_to_compromised)
            return roles_control_pb2.OperationResult(successful=True)

    def _get_item_by_id(self, db, model, id):
        id_query = uuid.UUID(id)
        return db.query(model).filter(model.id == id_query).first()
        
