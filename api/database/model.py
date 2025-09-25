from sqlmodel import Field, Session, SQLModel, create_engine, select
from auth import hash_password
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(SQLModel):
    username: str = Field(index=True)
    hashed_password: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class UserCreate(UserBase):
    pass

class UserPublic(UserBase):
    id: int

class DB():
    def __init__(self):
        sqlite_file_name = "database.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"

        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

    def create_db_and_tables(self):
        """
        Creates the SQLite database and tables
        """
        SQLModel.metadata.create_all(self.engine)

        # Add base admin user (TODO: create from environmental variable)
        if not self.find_user("dman3329"):
            self.add_user("dman3329", "password")

    def add_user(self, username, password):
        """
        Adds a user to the database

        Returns:
            Dict: Simple dictonary stating the user was created sucessfully
        """
        with Session(self.engine) as session:
            new_user = User(username=username, hashed_password=hash_password(password))
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return {"msg": "User created successfully"}
        
    def get_users(self):
        """
        Get a list of all users.

        Returns:
            List[User]: All user objects stored in the database.
        """
        with Session(self.engine) as session:
            users = session.exec(select(User)).all()
            return users
        
    def find_user(self, username):
        """
        Finds a specific user based on username

        Returns:
            User: User found(None otherwise)
        """
        with Session(self.engine) as session:
            return session.exec(select(User).where(User.username == username)).first()
