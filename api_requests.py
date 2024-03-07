import requests
import json

import os
import environ

env = environ.Env()
env.read_env(".env")


def create_user(name, phone, chat_id):
    url = f"{env.str('BASE_URL')}/auth/register/"
    response = requests.post(url=url,
                             json={
                                 'first_name': name,
                                 'phone': phone,
                                 'chat_id': chat_id
                             })

    return response


def check_user(chat_id):
    url = f"{env.str('BASE_URL')}/auth/check/"
    response = requests.get(url=url, json={'chat_id': chat_id})
    data = response.json()
    return data['status']


def get_user_id(chat_id):
    url = f"{env.str('BASE_URL')}/auth/check/"
    response = requests.get(url=url, json={'chat_id': chat_id})

    data = response.json()
    return data['user_id']


def feedback(chat_id, body):
    url = f"{env.str('BASE_URL')}/api/feedbacks/"
    user_id = get_user_id(chat_id)
    if body and user_id:
        post = requests.post(url=url, json={
            'user_id': user_id,
            'body': body
        })
        if post.status_code == 201:
            return True
    return False


def get_branches():
    url = f"{env.str('BASE_URL')}/api/branch-create/"
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def get_categories():
    url = f"{env.str('BASE_URL')}/api/category-list/"
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def get_products():
    url = f"{env.str('BASE_URL')}/api/product-list/"
    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def get_products_by_category(category_id):
    url = f"{env.str('BASE_URL')}/api/product-list/?category_id={category_id}"

    response = requests.get(url=url)
    if response.status_code == 200:
        data = response.json()
        return data
    return None

