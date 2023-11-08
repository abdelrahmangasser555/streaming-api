import os

from langchain.agents import load_tools, Tool
from langchain.tools import StructuredTool
import requests
from pydantic import BaseModel, Field
from langchain.vectorstores.base import VectorStoreRetriever, VectorStore
from enum import Enum

class SingleInputToolSchema(BaseModel):
    query: str = Field(..., min_length=1)


class SendToMakeArgsSchema(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=2)

class MakeABookingArgsSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the person who wants to make a booking")
    phone: str = Field(..., min_length=2, description="Phone number of the person who wants to make a booking")
    email: str = Field(..., min_length=2, description="Email of the person who wants to make a booking")
    message: str = Field(..., min_length=2, description="Message of the person who wants to make a booking")


def generate_dummy_ecommerce_products_homes(query):
    data = """1) colored pencil set
    2) holder for colored pencils
    3) cleaning brush
    4) baby bottle
    5) baby bottle holder
    6) school bag
    7) dispenser for liquid soap
    """
    return data


def send_dummy_image_url(query):
    message = "Send the below image without any modifications.\n"
    message+= "the image will be in the markdown format.\n"
    message+= "![image](https://i.imgur.com/3QX9q1j.jpeg)"
    return message


def send_telegram_message(query):
    telegram_api = os.environ["TELEGRAM_BOT_API"]
    url = f"https://api.telegram.org/bot{telegram_api}/sendMessage"
    data = {"chat_id": "1719079956", "text": query}

    response = requests.post(url, data=data)
    return "Message sent!"


def send_to_make(name, email):
    make_api = os.environ["MAKE_API"]
    url = f'https://hook.eu2.make.com/{make_api}'

    json = {
        "name": name,
        "email": email,
    }

    response = requests.post(url, json=json)
    if response.text == "Accepted":
        return "Data saved successfully!"


def make_a_booking(name, phone, email, message):
    url = "https://hook.eu2.make.com/u8sxe79c223tx3pr2o9uav4pcicyzja2"

    json = {
        "name": name,
        "phone": phone,
        "email": email,
        "message": message
    }

    response = requests.post(url, json=json)
    if response.text == "Accepted":
        return "Data saved successfully! (We will contact you soon)"

def _get_llm_math(llm):
    return load_tools(["llm-math"], llm=llm)[0]


def docs_to_text_retriever(retriever, custom_instruction=None):
    def _retriever(query):
        print(f"-----------{query}-----------")
        docs = retriever(query)
        text = custom_instruction or "Answer about the context below:\n\n"
        for d in docs:
            text += f"content:\n{d.page_content.strip()}\nmetadata_about_content:\n{d.metadata}\n\n"

        return text

    return _retriever

def docs_to_image_retriever(retriever, custom_instruction=None):
    def _retriever(query):
        pass

    return _retriever

def image_sender(query, user_question):
    # get images from the database
    # generate an AI response from the user question
    # send the images and the AI response to the user
    """
    {"image": "image_url", "description"
    :param query:
    :param user_question:
    :return:
    """


def _get_retriever(vectorstore: VectorStore, name, description, metadata=None, custom_instruction=None, image=False):
    if metadata:
        retriever = vectorstore.as_retriever(search_kwargs = {"filter": metadata})
    else:
        retriever = vectorstore.as_retriever()

    # if image:
    #     _retriever = docs_to_image_retriever(retriever.get_relevant_documents, custom_instruction)
    # else:
    _retriever = docs_to_text_retriever(retriever.get_relevant_documents, custom_instruction)

    return StructuredTool(
        name=name,
        description=description,
        func=_retriever,
        args_schema=SingleInputToolSchema,
        return_direct=image,
    )


def _get_telegram_tool(description=None):
    return StructuredTool(
        name="send_telegram_message",
        description=description or "Used to submit user info (name, email, phone number) and send any other kind of messages or updates to the owner of the jewelry store.",
        func=send_telegram_message,
        args_schema=SingleInputToolSchema,
    )


def _get_dummy_image_tool():
    return StructuredTool(
        name="image_getter_tool",
        description="Use this tool to look for image id of an image using its description",
        func=send_dummy_image_url,
        args_schema=SingleInputToolSchema,
        return_direct = True,
    )


def _get_make_tool():
    return StructuredTool(
        name="save_user_data",
        description="Use this tool to save user PROVIDED data (name, phone, email, message) to book an appointment, nothing can be empty.",
        func=send_to_make,
        args_schema=SendToMakeArgsSchema,
    )

def _get_make_a_booking_tool():
    return StructuredTool(
        name="make_a_booking",
        description="Use this tool to save user PROVIDED data (name, email,) to the excel sheet, name and email can't be empty.",
        func=make_a_booking,
        args_schema=MakeABookingArgsSchema,
    )

def _get_dummy_products_tool():
    return StructuredTool(
        name="products_database",
        description="Use this tool to get the list of products in the database",
        func=generate_dummy_ecommerce_products_homes,
        args_schema=SingleInputToolSchema,
    )


class AgentTool(str, Enum):
    CALCULATOR = "calculator"
    RETRIEVER = "retriever"
    TELEGRAM = "telegram"
    IMAGE = "image"
    MAKE = "make"
    PRODUCTS = "products"
    SEND_QUESTION = "send_question"
    MAKE_A_BOOKING = "make_a_booking"

tool_dict = {
    AgentTool.CALCULATOR: _get_llm_math,
    AgentTool.RETRIEVER: _get_retriever,
    AgentTool.TELEGRAM: _get_telegram_tool,
    AgentTool.IMAGE: _get_dummy_image_tool,
    AgentTool.MAKE: _get_make_tool,
    AgentTool.PRODUCTS: _get_dummy_products_tool,
    AgentTool.SEND_QUESTION: _get_telegram_tool,
    AgentTool.MAKE_A_BOOKING: _get_make_a_booking_tool,
}

def get_tool(tool_name):
    return tool_dict[tool_name]

