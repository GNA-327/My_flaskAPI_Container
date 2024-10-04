from flask import Blueprint, request, jsonify, current_app
import pandas as pd
from bson.objectid import ObjectId
import redis
import os

app_bp = Blueprint('app_bp', __name__)

@ app_bp.route('/upload_csv1', methods=['POST'])
def upload_csv1():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Selected file must be a CSV file"}), 400

    temp_file_path = os.path.join('uploads', file.filename)
    file.save(temp_file_path)

    try:
        df = pd.read_csv(temp_file_path)

        # Access Redis from current_app
        redis_client = current_app.redis_client

        for index, row in df.iterrows():
            redis_client.hmset(f"user:{index}", row.to_dict())

        return jsonify({"message": "CSV data inserted successfully into Redis"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "The uploaded file must be a CSV file"}), 400

    try:
        df = pd.read_csv(file)

        records = df.to_dict(orient='records')

        # Access MongoDB from current_app
        mongo_client = current_app.mongo_client
        db = mongo_client['flask_app_db']
        collection = db['users']

        collection.insert_many(records)

        return jsonify({"message": "CSV file successfully processed and data inserted into MongoDB!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route("/fetch_csv", methods=['GET'])
def fetch():
    try:
        mongo_client = current_app.mongo_client
        db = mongo_client['flask_app_db']
        collection = db['users']

        users = collection.find({'Age': {'$gt': 40, '$lt': 45}}, {'_id': 0})
        list_users = list(users)

        return jsonify({'users': list_users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ app_bp.route("/fetch_csv1", methods=['GET'])
def fetch1():
    try:
        redis_client = current_app.redis_client
        users = []
        keys = redis_client.keys('user:*')
        for key in keys:
            user = redis_client.hgetall(key)
            user = {k.decode('utf-8'): v.decode('utf-8') for k, v in user.items()}
            users.append(user)
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ app_bp.route('/delete_mongodb', methods=['DELETE'])
def delete_user():
    try:
        age = request.args.get('age', type=int)
        if age is None:
            return jsonify({"error": "Age parameter is required."}), 400

        mongo_client = current_app.mongo_client
        db = mongo_client['flask_app_db']
        collection = db['users']

        result = collection.delete_many({'Age': age})

        return jsonify({"success": f"Successfully deleted {result.deleted_count} users with Age {age}."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route('/delete_redis', methods=['DELETE'])
def delete_user1():
    try:
        user_id = request.args.get('id')
        if not user_id:
            return jsonify({'error': 'id parameter not provided'}), 400

        redis_client = current_app.redis_client
        redis_client.delete(f"user:{user_id}")
        return jsonify({"success": f"Successfully deleted {user_id} from Redis"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route('/update_mongo_user', methods=['PUT'])
def update_user_mongo():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    user_id = data.get('_id')
    fields = data.get('fields')

    if not user_id or not fields:
        return jsonify({"error": "Both '_id' and 'fields' are required."}), 400

    try:
        object_id = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid '_id' format."}), 400

    try:
        mongo_client = current_app.mongo_client
        db = mongo_client['flask_app_db']
        collection = db['users']

        result = collection.update_one({"_id": object_id}, {"$set": fields})

        if result.matched_count == 0:
            return jsonify({"error": f"No user found with _id '{user_id}'."}), 404
        elif result.modified_count == 0:
            return jsonify({"message": f"No changes made to the user with _id '{user_id}'."}), 200
        else:
            return jsonify({"message": f"User with _id '{user_id}' updated successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route('/update_all_mongo_user', methods=['PUT'])
def update_all_user_mongo():
    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "No data provided"}), 400
    fields = update_data.get('fields')
    if not fields:
        return jsonify({"Error": "'fields' is required"}), 400
    try:
        mongo_client = current_app.mongo_client
        db = mongo_client['flask_app_db']
        collection = db['users']

        result = collection.update_many({}, {"$set": fields})
        return jsonify({"success": f"Updated {result.modified_count} documents in the 'users' collection."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route('/update_all_users_mongo', methods=['PUT'])
def update_all_users_mongo():
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json"}), 415
    data = request.get_json()

    fields = data.get('fields')

    if not fields:
        return jsonify({"error": "'fields' is required."}), 400

    try:
        mongo_client = current_app.mongo_client
        db = mongo_client['flask_app_db']
        collection = db['users']

        result = collection.update_many({}, {"$set": fields})

        return jsonify({
            "message": f"Updated {result.modified_count} documents in the 'users' collection."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ app_bp.route('/update_redis', methods=['PUT'])
def update_user_redis():
    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "No fields provided"}), 400
    user_id = update_data.get('id')
    fields = update_data.get('fields')
    if not user_id or not fields:
        return jsonify({"error": "Both 'id' and 'fields' are required"}), 400

    try:
        redis_client = current_app.redis_client
        redis_key = f"user:{user_id}"
        if not redis_client.exists(redis_key):
            return jsonify({"error": f"No user found with ID {user_id} in Redis"}), 400

        redis_client.hmset(redis_key, fields)
        return jsonify({"message": f"User with ID {user_id} updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
