from flask import jsonify

def respond(data=None, error=None, detail=None):
    if error:
        response = {
            "error": {
                "code": error,
                "detail": detail,
            }
        }
    else:
        response = {
            "data": data,
        }

    return jsonify(response)