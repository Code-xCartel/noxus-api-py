from app.core.bound_repository import BoundRepository


class RepoHelpersMixin:
    repo: BoundRepository

    def __init__(
        self,
        repo: BoundRepository,
    ):
        self.repo = repo

    @property
    def api_config(self):
        return self.repo.api_config

    @property
    def auth_utils(self):
        return self.repo.auth_utils

    @property
    def user_realm(self):
        return self.repo.user_realm

    @property
    def nox_id(self):
        return self.user_realm.nox_id

    @property
    def email(self):
        return self.user_realm.email

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
