from fastapi import Request

from app.core.bound_repository import BoundRepository
from app.core.config import ApiConfig


class RepoHelpersMixin:
    repo: BoundRepository
    api_config: ApiConfig

    def __init__(
        self, repo: BoundRepository, api_config: ApiConfig, request: Request = None
    ):
        self.repo = repo
        self.api_config = api_config
        self.request = request

    def insert_one(self, *args, **kwargs):
        return self.repo.insert_one(*args, **kwargs)

    def get_one(self, *args, **kwargs):
        return self.repo.get_one(self, *args, **kwargs)

    def get_one_by_query(self, *args, **kwargs):
        return self.repo.get_one_by_query(self, *args, **kwargs)

    def update_one(self, *args, **kwargs):
        return self.repo.update_one(self, *args, **kwargs)

    def delete_one(self, *args, **kwargs):
        return self.repo.delete_one(self, *args, **kwargs)
