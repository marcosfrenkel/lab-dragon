import json
import uuid
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Union, Tuple, List


from ..utils import create_timestamp
from .table import Table


class SupportedCommentType(Enum):
    """
    Enum that holds the supported types of comments. This is used to classify the comment type.
    """

    md = 1
    string = 2
    jpg = 4
    png = 5
    table = 6

    @classmethod
    def classify(cls, item: Union[Path, str]) -> int:
        """
        Classifies the comment type based on the extension of the file.

        :param item: The text of the comment we are classifying.
        :return: The numerical value representing the comment type of the enum,
        """

        if isinstance(item, Table):
            return SupportedCommentType.table.value

        # If the item is not a path, check if it's longer than 256 characters.
        # If it is, it is a string.
        # If it is not, convert it to a path to see if it has an extension.
        if not isinstance(item, Path):
            if len(item) > 256:
                return SupportedCommentType.string.value

            item = Path(item)
        ext = item.suffix
        try:
            return cls[ext[1:]].value
        except KeyError as e:
            # if there is a KeyError it means it cannot find the extension, so the comment is not treated as a file.
            pass

        return SupportedCommentType.string.value


class Comment:
    """
    Class that holds all the versions of a _single_ comment. This is used to keep track of the history of a comment.
    All comments and modification need to also include the user that made the comment or modification.
    When the comment is created or modified, a timestamp is also stored as well as its comment classification.

    To get the current version of the comment, the method `get_current_comment` should be used.
    This method will return a tuple with the comment itself, the type, the author and the timestamp.

    When reconstructing a Comment instance from a comment inside a file, simply put the recorded string in a JSON loads,
    and pass the resulting dictionary to the constructor as kwargs.

    A few fields are also present holding extra meta-data. These are:

    - ID: The unique ID of the comment. This is assigned at creation.
        Used to keep track of the same comment through a save file
    - user: The original user that created the comment.
        This should not be changed, since every modification also stores its author.
    - created: The time when the comment was originally created.
    - deleted: A boolean indicating if the comment has been deleted.
        We should never delete a comment, but this will mark if the comment should be displayed or not.

    :param content: The content of the comment. This can be a string or a path.
    :param user: The user that created the comment.
    """
    def __init__(self, content: Union[List[Union[str, Path, Table]], Union[str, Path, Table]], creation_user: str, **kwargs):
        if len(kwargs) != 0:
            self.ID = kwargs['ID']
            self.creation_user = creation_user
            self.created = kwargs['created']
            self.deleted = kwargs['deleted']
            self.dates = kwargs['dates']
            self.authors = kwargs['authors']
            self.com_type = kwargs['com_type']
            self.content = content
            # If the text is a dictionary, convert it into a table object
            table_indices = [index for index, value in enumerate(self.com_type) if value == 6]
            if len(table_indices) != 0:
                for i in table_indices:
                    self.content[i] = Table(**content[i])

        else:
            self.ID = str(uuid.uuid4())
            self.creation_user = creation_user
            time = create_timestamp()
            self.created = time
            self.deleted = False
            self.content = [content if isinstance(content, Table) else str(content)]
            self.dates = [time]
            self.authors = [creation_user]
            self.com_type = [SupportedCommentType.classify(content)]

    def modify(self, content: Union[str, Path, Table], user: str) -> None:
        """
        Modify the comment.
        This will check if the content or user are different
        and append the new comment to the list of comments and update the timestamp.
        Passing the user is required.

        :param content: The actual comment.
        :param user: The user that wrote the comment
        """

        if content != self.content[-1] or user != self.authors[-1]:
            self.content.append(content)
            time = create_timestamp()
            self.dates.append(time)
            self.authors.append(user)
            self.com_type.append(SupportedCommentType.classify(content))

    # TODO: This might be obsolete since in theory the last index should always be the latest comment.
    #  I am not fully convinced that this is the case though.
    def last_comment_index(self) -> int:
        """
        Function indicating the index of the last comment that was made.

        :return: The index indicating the position of the last comment
        """
        most_recent_index = 0
        most_recent_time = None

        dates_set = set(self.dates)

        # Since this comment object should hold a single comment, there is almost no way a comment should be edited
        # in the exact same time as it is created. This would mean that someone is trying to store multiple comments
        # in the same object instead of multiple versions.
        if len(self.dates) != len(dates_set):
            raise ValueError("There are multiple comments with the same timestamp.")

        for index, time_str in enumerate(self.dates):
            try:
                time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
                if most_recent_time is None or time_obj > most_recent_time:
                    most_recent_time = time_obj
                    most_recent_index = index
            except ValueError:
                pass  # Ignore invalid time strings

        return most_recent_index

    def last_comment(self) -> Tuple[str, int, str, str]:
        """
        Function returning the last comment that was made. The return object is a tuple containing in order:
        - The last comment.
        - The numerical code indicating the type of comment (check the SupportedCommentType enum).
        - The user that made the last comment.
        - The timestamp of the last comment.

        :return: A tuple containing the last comment and the user that made it.
        """
        index = self.last_comment_index()
        return self.content[index], self.com_type[index], self.authors[index], self.dates[index]

    def __str__(self):
        ret = self.__dict__.copy()
        return json.dumps(ret)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
