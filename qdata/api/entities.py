import json
from enum import Enum, auto
from pathlib import Path

from flask import abort, make_response, send_file

from qdata.modules.task import Task
from qdata.modules.step import Step
from qdata.modules.project import Project
from qdata.modules.instance import Instance
from qdata.generators.meta import read_from_TOML
from qdata.components.comment import SupportedCommentType, Comment

ROOTPATH = Path(r'/Users/marcosf2/Documents/github/qdata-mockup/test/env_generator/Testing Project.toml')

INDEX = {}

PATHINDEX = {}

# Inside the image index the string to identify the image is the ID of the entity + '--' + the name of the image
IMAGEINDEX = {}


def get_indices():

    index = json.dumps(str(INDEX))
    imageindex = json.dumps(str(IMAGEINDEX))

    ret = {'index': index, 'imageindex': imageindex, 'pathindex': PATHINDEX}
    return ret


class MediaTypes(Enum):
    """
    Enum that contains the different types of images that are supported
    """
    png = auto()
    jpg = auto()
    md = auto()

    @classmethod
    def is_supported(cls, media_path):
        media_path = Path(media_path)
        if media_path.suffix[1:] in cls.__members__:
            return True
        else:
            return False


def _reset_indices():
    global INDEX
    global IMAGEINDEX
    global PATHINDEX

    INDEX = {}
    IMAGEINDEX = {}
    PATHINDEX = {}


# TODO: This reshuffling of comments is breaking the order in which comments are displayed in the UI.
#  Order should be maintained even when expanding folders.
def read_child_entity(entity_path: Path):

    ent = read_from_TOML(entity_path)
    if ent.ID not in INDEX:
        INDEX[ent.ID] = ent

    if entity_path not in PATHINDEX:
        PATHINDEX[str(entity_path)] = ent.ID

    child_list = []
    if len(ent.children) > 0:
        for child in ent.children:
            child_list.append(read_child_entity(child))

    ret_dict = {"id": ent.ID,
                "name": ent.name,
                "type": ent.__class__.__name__,
                "children": child_list,
                }

    return ret_dict


def read_all():
    """
    Function that reads all the entities and return a dictionary with nested entities
    :return:
    """

    # Create the return dictionary
    ret = [read_child_entity(ROOTPATH)]

    # We replace the parent and children after we are done going through all identities to make sure that
    # the parent is already in the index, there might be edge cases where a lower entity in the tree has a parent
    # somewhere else (probably more important once we start allowing branching)

    # Update the parent of the children
    for key, val in INDEX.items():
        path = Path(val.parent)
        if path.is_file():
            val.parent = PATHINDEX[str(path)]

        # Update the children of the parent
        for child in val.children:
            path = Path(child)
            if path.is_file():
                val.children[val.children.index(child)] = PATHINDEX[str(path)]

    return ret


def read_one(ID, name_only=False):
    """
    API function that returns an entity based on its ID
    """

    if ID not in INDEX:
        read_all()

    if ID in INDEX:
        ent = INDEX[ID]

        if name_only:
            return ent.name

        return json.dumps(ent.to_TOML()[ent.name]), 201
    else:
        abort(404, f"Entity with ID {ID} not found")


def read_image(ID, imageName):
    """
    API function that returns an image based on the ID of the entity and the name of the image
    """

    if ID + '--' + imageName in IMAGEINDEX:
        image = IMAGEINDEX[ID + '--' + imageName]
        return send_file(image)
    else:
        abort(404, f"Image with ID {ID} and name {imageName} not found")


def read_comment(ID, commentID):
    """
    API function that looks at the comment ID of the entity with ID and returns the comment

    :param ID:
    :param commentID:
    :return:
    """

    if ID not in INDEX:
        abort(404, f"Entity with ID {ID} not found")

    ent = INDEX[ID]
    ids = [c.ID for c in ent.comments]
    if commentID not in ids:
        abort(404, f"Comment with ID {commentID} not found")
    ind = ids.index(commentID)
    if ind == -1:
        abort(404, f"Comment with ID {commentID} not found")
    comment = ent.comments[ind]
    content, media_type, author, date = comment.last_comment()
    if media_type == SupportedCommentType.jpg.value or media_type == SupportedCommentType.png.value:
        return send_file(content)
    else:
        return json.dumps(content), 201


def add_comment(ID, comment):

    ent = INDEX[ID]
    ent.comments.append(comment['text'])
    path = None
    for key, val in PATHINDEX.items():
        if val == ID:
            path = key
            break

    if path is None:
        return abort(404, f"Could not find the original location of entity")

    ent.to_TOML(path)
    return make_response("Comment added", 201)

