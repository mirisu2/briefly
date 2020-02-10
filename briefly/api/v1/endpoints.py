# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from briefly import redis_client
import sqlalchemy
from sqlalchemy import text
from briefly.models.users import Users
from briefly.models.authors import Authors
from briefly import db


bp = Blueprint('api', __name__, url_prefix='/api/v1')


@bp.before_request
def check_api_header():
    token = request.headers.get('X-AUTHOR-API-Key')
    if not token:
        return jsonify({
            'error': 'The request header does not have an API access key'}), 403
    if token:
        if not redis_client.get(token):
            is_token_present = Users.query.filter_by(user_token=token).first()
            if is_token_present is None:
                return jsonify({'error': 'Forbidden'}), 403
            else:
                redis_client.set(token, '1')
                redis_client.expire(token, 600)


@bp.route('/authors', methods=['GET'])
def get_all_authors():
    response_ = {
        'number_of_records': 0,
        'authors': []
    }
    authors = Authors.query.all()
    if authors:
        response_['number_of_records'] = len(authors)
        for author in authors:
            response_['authors'].append({
                'id': author.id,
                'author_fullname': author.author_fullname,
                'author_url': author.author_url
            })

    return jsonify(response_), 200


@bp.route('/authors/<int:id>', methods=['GET'])
def get_by_id(id):
    if id:
        response_ = {
            'author': {}
        }
        author = Authors.query.filter_by(id=id).first()
        if author:
            response_['author'] = {
                'id': author.id,
                'author_fullname': author.author_fullname,
                'author_url': author.author_url
            }
            return jsonify(response_), 200
        else:
            return jsonify({'error': 'Not Found'}), 404


@bp.route('/authors', methods=['POST'])
def post():
    body = request.get_json(force=True)
    author_fullname = body['author_fullname']
    author_url = body['author_url']
    try:
        new_author = Authors(author_fullname=author_fullname, author_url=author_url)
        db.session.add(new_author)
        db.session.commit()
        return jsonify({'Status': 'Success', 'author_id': new_author.id}), 200
    except sqlalchemy.exc.IntegrityError:
        return jsonify({'error': 'Duplicate entry'}), 500


@bp.route('/authors/<int:id>', methods=['PUT'])
def put(id):
    body = request.get_json(force=True)
    author = Authors.query.filter_by(id=id).first()
    if author:
        author.author_fullname = body['author_fullname']
        author.author_url = body['author_url']
        db.session.commit()
        return jsonify({'Status': 'Success'}), 200
    else:
        return jsonify({'error': 'Not Found'}), 404


@bp.route('/authors/<int:id>', methods=['DELETE'])
def delete(id):
    delete_author = Authors.query.filter_by(id=id).first()
    if delete_author:
        db.session.delete(delete_author)
        db.session.commit()
        return jsonify({'Status': 'Success'}), 200
    else:
        return jsonify({'Error': 'Not Found'}), 404
